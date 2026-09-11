"""Google Cloud Remote MCP Agent using Google Agent Development Kit (ADK).

This agent connects directly to official Google Cloud Remote MCP Server
endpoints (e.g. recommender.googleapis.com/mcp) using ADK's native McpToolset.
No custom JSON-RPC client code is needed.
"""

import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict
import yaml
from fastapi import FastAPI, HTTPException, Request as FastAPIRequest
from fastapi.responses import JSONResponse, StreamingResponse
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.genai import types
from google.adk.features import FeatureName, override_feature_enabled

# Disable JSON_SCHEMA_FOR_FUNC_DECL to prevent Vertex AI schema flattening limits
override_feature_enabled(FeatureName.JSON_SCHEMA_FOR_FUNC_DECL, False)

logger = logging.getLogger(__name__)

# Catalog of Google Cloud remote MCP server endpoints
# Reference: https://docs.cloud.google.com/mcp/supported-products
MCP_CATALOG: Dict[str, str] = {
    "recommender": "https://recommender.googleapis.com/mcp",
    "compute": "https://compute.googleapis.com/mcp",
    "bigquery": "https://bigquery.googleapis.com/mcp",
    "cloudbilling": "https://cloudbilling.googleapis.com/mcp",
    "run": "https://run.googleapis.com/mcp",
    "storage": "https://storage.googleapis.com/storage/mcp",
    "secops": os.getenv("SECOPS_MCP_URL", "https://us-chronicle.googleapis.com/mcp"),
}

# Active service configuration
SERVICE_NAME = os.getenv("ACTIVE_MCP_SERVICE", "recommender").lower()
MCP_URL = os.getenv(
    "MCP_SERVER_URL", MCP_CATALOG.get(SERVICE_NAME, MCP_CATALOG["recommender"])
)
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")


def get_auth_headers(ctx=None) -> Dict[str, str]:
    """Provide fresh Google Cloud OAuth2 Bearer token for remote MCP calls.

    ADK invokes this callable dynamically for each tool request, ensuring
    tokens never go stale during long-running sessions.
    """
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }

    # When authenticating via local Application Default Credentials (user account),
    # Google Cloud APIs like Recommender require a billing/quota project header.
    quota_project = (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or getattr(credentials, "quota_project_id", None)
        or project
    )
    if quota_project:
        headers["X-Goog-User-Project"] = quota_project

    return headers


def _parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Extract and parse YAML frontmatter from markdown content."""
    stripped = content.strip()
    if not stripped.startswith("---"):
        return {}
    parts = stripped.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data = yaml.safe_load(parts[1])
        return data if isinstance(data, dict) else {}
    except Exception as err:
        logger.warning(f"Failed to parse YAML frontmatter: {err}")
        return {}


def _get_skills_dir(service_name: str | None = None) -> Path | None:
    """Resolve skills directory for a given service."""
    svc = (service_name or SERVICE_NAME).lower()
    candidates = [
        Path(__file__).resolve().parent.parent / "skills" / svc,
        Path(__file__).resolve().parent / "skills" / svc,
        Path.cwd() / "skills" / svc,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def get_secops_skill_tools(skill_name: str | None = None) -> list[str]:
    """Read YAML frontmatter from skills/secops/ to collect tool_filter definitions.

    If skill_name is given, returns that skill's tools. If None, aggregates
    unique tools across all skills in skills/secops/ (or falls back to
    MCP_TOOL_FILTER if set).
    """
    skills_dir = _get_skills_dir("secops")
    if skills_dir is None or not skills_dir.exists():
        raw_filter = os.getenv("MCP_TOOL_FILTER", "").strip()
        if raw_filter:
            return [t.strip() for t in raw_filter.split(",") if t.strip()]
        return []

    # Collect skill files: root SKILL.md first, then subdirectories, then TEMPLATE.md
    main_skill = skills_dir / "SKILL.md"
    skill_files: list[Path] = []
    if main_skill.exists():
        skill_files.append(main_skill)

    sub_skills = sorted(
        [p for p in skills_dir.rglob("SKILL.md") if p.is_file() and p != main_skill],
        key=lambda p: str(p.relative_to(skills_dir)),
    )
    skill_files.extend(sub_skills)

    template_file = skills_dir / "TEMPLATE.md"
    if template_file.exists():
        skill_files.append(template_file)

    if skill_name is not None:
        target = skill_name.strip().lower().replace("_", "-")
        for file_path in skill_files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError as err:
                logger.warning(f"Could not read skill file {file_path}: {err}")
                continue
            meta = _parse_yaml_frontmatter(content)
            name = str(meta.get("name", "")).strip().lower().replace("_", "-")
            parent_dir = file_path.parent.name.strip().lower().replace("_", "-")
            stem = file_path.stem.strip().lower().replace("_", "-")
            rel_dir = (
                str(file_path.relative_to(skills_dir).parent)
                .strip()
                .lower()
                .replace("_", "-")
            )

            if target in (name, parent_dir, stem, rel_dir):
                tools = meta.get("tool_filter", [])
                if isinstance(tools, list):
                    return [str(t).strip() for t in tools if str(t).strip()]
                return []
        return []

    # Aggregate across active SKILL.md files (excluding template)
    aggregated_tools: list[str] = []
    active_skill_files = [p for p in skill_files if p.name == "SKILL.md"]
    for file_path in active_skill_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as err:
            logger.warning(f"Could not read skill file {file_path}: {err}")
            continue
        meta = _parse_yaml_frontmatter(content)
        tools = meta.get("tool_filter", [])
        if isinstance(tools, list):
            for tool in tools:
                tool_name_str = str(tool).strip()
                if tool_name_str and tool_name_str not in aggregated_tools:
                    aggregated_tools.append(tool_name_str)

    if not aggregated_tools:
        raw_filter = os.getenv("MCP_TOOL_FILTER", "").strip()
        if raw_filter:
            return [t.strip() for t in raw_filter.split(",") if t.strip()]

    return aggregated_tools


def load_instructions(service_name: str | None = None) -> str:
    """Load and aggregate skill instructions and catalog for the active service."""
    svc = (service_name or SERVICE_NAME).lower()
    skills_dir = _get_skills_dir(svc)
    default_instruction = (
        f"You are a helpful assistant with access to Google Cloud {svc} tools."
    )
    if skills_dir is None or not skills_dir.exists():
        return default_instruction

    main_skill = skills_dir / "SKILL.md"
    main_content = ""
    if main_skill.exists():
        try:
            main_content = main_skill.read_text(encoding="utf-8").strip()
        except OSError as err:
            logger.warning(f"Could not read main skill file {main_skill}: {err}")

    if not main_content:
        main_content = default_instruction

    # Look for sub-skills in subdirectories
    sub_skill_files = sorted(
        [p for p in skills_dir.rglob("SKILL.md") if p.is_file() and p != main_skill],
        key=lambda p: str(p.relative_to(skills_dir)),
    )

    if not sub_skill_files:
        return main_content

    # Index and aggregate sub-skills
    catalog_lines = [
        "",
        "---",
        "",
        "## Specialized Sub-Skills Catalog",
        "",
        "The following specialized sub-skills and runbooks are available for domain workflows:",
    ]
    detailed_sections = []

    for sub_file in sub_skill_files:
        try:
            content = sub_file.read_text(encoding="utf-8")
        except OSError as err:
            logger.warning(f"Could not read sub-skill file {sub_file}: {err}")
            continue

        meta = _parse_yaml_frontmatter(content)
        name = meta.get("name", sub_file.parent.name)
        role = meta.get("role", "")
        category = meta.get("category", "")
        description = meta.get("description", "").strip().rstrip(".")
        tool_filter = meta.get("tool_filter", [])
        tool_str = ", ".join(f"`{t}`" for t in tool_filter) if tool_filter else "None"

        role_info = (
            f" (Role: {role}, Category: {category})" if (role or category) else ""
        )
        desc_info = f": {description}" if description else ""
        catalog_lines.append(
            f"- **{name}**{role_info}{desc_info}. Scoped Tools: {tool_str}"
        )

        body = content.strip()
        if body.startswith("---"):
            parts = body.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()

        detailed_sections.append(f"### Sub-Skill: {name}\n\n{body}")

    detailed_block = ""
    if detailed_sections:
        detailed_block = (
            "\n\n---\n\n## Detailed Sub-Skill Runbooks\n\n"
            + "\n\n---\n\n".join(detailed_sections)
        )

    return main_content + "\n" + "\n".join(catalog_lines) + detailed_block


_tool_filter_raw = os.getenv("MCP_TOOL_FILTER", "").strip()
if _tool_filter_raw:
    TOOL_FILTER = [t.strip() for t in _tool_filter_raw.split(",") if t.strip()] or None
elif SERVICE_NAME == "secops":
    TOOL_FILTER = get_secops_skill_tools() or None
else:
    TOOL_FILTER = None

# Define the ADK Agent
# ADK automatically handles tool discovery (tools/list), parameter mapping,
# function calling execution, and response synthesis.
root_agent = Agent(
    name=f"gcp_{SERVICE_NAME}_agent",
    model=MODEL_NAME,
    instruction=load_instructions(),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=MCP_URL),
            header_provider=get_auth_headers,
            tool_filter=TOOL_FILTER,
        )
    ],
)

# FastAPI application serving Agent Runtime and health probes
app = FastAPI(title=f"GCP {SERVICE_NAME.capitalize()} Reasoning Engine")

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="gcp_agent", session_service=session_service)


@app.get("/")
@app.get("/health")
@app.get("/healthz")
async def health_check():
    return {"status": "ok", "agent": root_agent.name}


def _parse_reasoning_engine_input(body: Dict[str, Any]):
    """Extract (class_method, kwargs, user_id, session_id, content, is_gemini_enterprise) from Reasoning Engine payload."""
    class_method = body.get("class_method", "")
    kwargs = body.get("input", {}) or {}

    user_id = kwargs.get("user_id") or kwargs.get("userId")
    session_id = kwargs.get("session_id") or kwargs.get("sessionId")
    raw_message = kwargs.get("message")
    is_gemini_enterprise = (class_method == "streaming_agent_run_with_events") or (
        "request_json" in kwargs
    )

    if "request_json" in kwargs:
        try:
            req_data = json.loads(kwargs["request_json"])
            user_id = req_data.get("user_id") or req_data.get("userId") or user_id
            session_id = (
                req_data.get("session_id") or req_data.get("sessionId") or session_id
            )
            if req_data.get("message") is not None:
                raw_message = req_data.get("message")
        except Exception as err:
            logger.warning(f"Could not parse request_json: {err}")

    user_id = user_id or "user"
    session_id = session_id or f"session_{int(time.time())}"

    # Build types.Content object correctly regardless of whether raw_message is dict, Content, or str
    if isinstance(raw_message, types.Content):
        content = raw_message
    elif isinstance(raw_message, dict):
        try:
            content = types.Content(**raw_message)
        except Exception:
            parts_data = raw_message.get("parts", [])
            parts = []
            for p in parts_data:
                if isinstance(p, dict) and "text" in p:
                    parts.append(types.Part.from_text(text=str(p["text"])))
                elif isinstance(p, str):
                    parts.append(types.Part.from_text(text=p))
            if not parts and "text" in raw_message:
                parts = [types.Part.from_text(text=str(raw_message["text"]))]
            content = types.Content(
                role=raw_message.get("role", "user"),
                parts=parts or [types.Part.from_text(text=str(raw_message))],
            )
    elif isinstance(raw_message, str):
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=raw_message)]
        )
    else:
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=str(raw_message or ""))]
        )

    return class_method, kwargs, user_id, session_id, content, is_gemini_enterprise


@app.post("/api/stream_reasoning_engine")
async def stream_reasoning_engine(request: FastAPIRequest):
    """Serve the Reasoning Engine streaming contract for the Vertex AI Console Playground and Gemini Enterprise."""
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    class_method, kwargs, user_id, session_id, content, is_ge = (
        _parse_reasoning_engine_input(body)
    )

    try:
        await session_service.create_session(
            app_name="gcp_agent", user_id=user_id, session_id=session_id
        )
    except Exception:
        pass

    async def event_generator():
        try:
            from vertexai.agent_engines import _utils
        except ImportError:
            from agentplatform._genai import _agent_engines_utils as _utils

        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                event_dict = _utils.dump_event_for_json(event)
                if is_ge:
                    # Gemini Enterprise streaming_agent_run_with_events contract
                    chunk = {
                        "events": [event_dict],
                        "session_id": session_id,
                        "artifacts": [],
                    }
                    yield json.dumps(chunk) + "\n"
                else:
                    # Vertex AI Console Playground / SDK stream_query contract
                    yield json.dumps(event_dict) + "\n"
        except Exception as exc:
            logger.error(
                f"Error during streaming reasoning engine execution: {exc}",
                exc_info=True,
            )
            if is_ge:
                err_event = {
                    "content": {"parts": [{"text": f"Error: {exc}"}], "role": "agent"},
                    "author": "agent",
                    "actions": {},
                }
                yield (
                    json.dumps(
                        {
                            "events": [err_event],
                            "session_id": session_id,
                            "artifacts": [],
                        }
                    )
                    + "\n"
                )
            raise

    return StreamingResponse(event_generator(), media_type="application/json")


@app.post("/api/reasoning_engine")
async def reasoning_engine_query(request: FastAPIRequest):
    """Serve the Reasoning Engine synchronous contract."""
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    class_method, kwargs, user_id, session_id, content, _ = (
        _parse_reasoning_engine_input(body)
    )

    if class_method in ("create_session", "async_create_session"):
        session = await session_service.create_session(
            app_name="gcp_agent", user_id=user_id, session_id=session_id
        )
        return JSONResponse(content={"output": {"id": session.id, "user_id": user_id}})

    if class_method in ("get_session", "async_get_session"):
        session = await session_service.get_session(
            app_name="gcp_agent", user_id=user_id, session_id=session_id
        )
        if session:
            return JSONResponse(
                content={"output": {"id": session.id, "user_id": user_id}}
            )
        return JSONResponse(content={"output": None})

    if class_method in ("list_sessions", "async_list_sessions"):
        sessions = await session_service.list_sessions(
            app_name="gcp_agent", user_id=user_id
        )
        return JSONResponse(content={"output": [s.id for s in (sessions or [])]})

    if class_method in ("delete_session", "async_delete_session"):
        await session_service.delete_session(
            app_name="gcp_agent", user_id=user_id, session_id=session_id
        )
        return JSONResponse(content={"output": None})

    try:
        await session_service.create_session(
            app_name="gcp_agent", user_id=user_id, session_id=session_id
        )
    except Exception:
        pass

    agent_response_text = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    agent_response_text = event.content.parts[0].text
    except Exception as exc:
        logger.error(f"Error during reasoning engine query: {exc}", exc_info=True)
        return JSONResponse(
            content={"error": str(exc), "output": f"Execution error: {exc}"},
            status_code=500,
        )

    return JSONResponse(content={"output": agent_response_text})
