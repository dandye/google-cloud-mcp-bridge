"""Unit tests for SecOps skill definitions and YAML metadata validation."""

from pathlib import Path
import pytest
import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills" / "secops"

# Known tools exposed by official Chronicle Remote MCP server
KNOWN_CHRONICLE_MCP_TOOLS = {
    "activate_parser",
    "add_rows_to_data_table",
    "create_case_comment",
    "create_data_table",
    "create_feed",
    "create_parser",
    "create_reference_list",
    "create_rule",
    "deactivate_parser",
    "delete_data_table_row",
    "delete_feed",
    "disable_feed",
    "enable_feed",
    "evaluate_rule_coverage",
    "evaluate_rule_coverage_long_running",
    "execute_actions",
    "execute_bulk_close_case",
    "execute_manual_action",
    "fetch_alert_data",
    "fetch_enrichment_actions",
    "generate_feed_secret",
    "generate_rules",
    "generate_synthetic_events",
    "generate_threat_detection_opportunity",
    "get_agent_settings",
    "get_alert_latest_investigation",
    "get_case",
    "get_case_alert",
    "get_connector_event",
    "get_feed",
    "get_investigation_by_id",
    "get_involved_entity",
    "get_ioc_match",
    "get_operation",
    "get_parser",
    "get_reference_list",
    "get_rule",
    "get_security_alert",
    "import_logs",
    "list_case_alerts",
    "list_case_comments",
    "list_cases",
    "list_connector_events",
    "list_data_table_rows",
    "list_data_tables",
    "list_feeds",
    "list_integration_actions",
    "list_integration_instances",
    "list_integrations",
    "list_involved_entities",
    "list_log_types",
    "list_parsers",
    "list_playbook_instances",
    "list_playbooks",
    "list_rule_detections",
    "list_rule_errors",
    "list_rules",
    "list_security_alerts",
    "run_parser",
    "search_entity",
    "search_raw_logs",
    "summarize_entity",
    "translate_udm_query",
    "trigger_investigation",
    "udm_search",
    "update_case",
    "update_case_alert",
    "update_feed",
    "update_reference_list",
    "update_security_alert",
    "validate_rule",
}

# Domain-specific SecOps action mappings and valid aliases
VALID_TOOL_ALIASES = {
    "get_rule_detections",
    "get_ioc_matches",
    "add_case_comment",
    "list_reference_lists",
    "close_case",
}

VALID_SECOPS_TOOLS = KNOWN_CHRONICLE_MCP_TOOLS | VALID_TOOL_ALIASES

REQUIRED_MARKDOWN_SECTIONS = [
    "Overview",
    "Tool Scope",
    "Reasoning Protocol",
    "HITL",
    "Example Prompts",
    "Output Schema",
]


def get_skill_files() -> list[Path]:
    """Retrieve all SKILL.md and template files under skills/secops/ recursively."""
    files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    template = SKILLS_DIR / "TEMPLATE.md"
    if template.exists() and template not in files:
        files.append(template)
    return files


def get_skill_md_files() -> list[Path]:
    """Retrieve all SKILL.md files under skills/secops/ recursively."""
    return sorted(SKILLS_DIR.rglob("SKILL.md"))


def parse_yaml_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def test_secops_template_exists():
    """Verify skills/secops/TEMPLATE.md exists and is valid."""
    template_file = SKILLS_DIR / "TEMPLATE.md"
    assert template_file.exists(), "skills/secops/TEMPLATE.md must exist"
    content = template_file.read_text(encoding="utf-8")
    meta = parse_yaml_frontmatter(content)
    assert meta.get("name") == "secops-skill-template"
    assert "description" in meta
    assert "tool_filter" in meta
    assert isinstance(meta["tool_filter"], list)


@pytest.mark.parametrize(
    "skill_file", get_skill_files(), ids=lambda p: str(p.relative_to(SKILLS_DIR))
)
def test_skill_frontmatter_schema(skill_file: Path):
    """Verify each SecOps skill has valid YAML frontmatter conforming to schema."""
    content = skill_file.read_text(encoding="utf-8")
    meta = parse_yaml_frontmatter(content)
    assert meta, f"{skill_file} is missing YAML frontmatter"
    assert "name" in meta, f"{skill_file} missing 'name'"
    assert "description" in meta, f"{skill_file} missing 'description'"
    assert "role" in meta, f"{skill_file} missing 'role'"
    assert "category" in meta, f"{skill_file} missing 'category'"
    assert "tool_filter" in meta, f"{skill_file} missing 'tool_filter'"
    assert isinstance(meta["tool_filter"], list), (
        f"{skill_file} 'tool_filter' must be a list"
    )
    assert len(meta["tool_filter"]) > 0, (
        f"{skill_file} 'tool_filter' must contain at least one tool"
    )
    for tool in meta["tool_filter"]:
        assert isinstance(tool, str) and tool.strip(), (
            f"Invalid tool name in {skill_file}: {tool}"
        )


def test_imported_skills_exist():
    """Verify all 3 imported agentic_soc skills exist in skills/secops/."""
    expected_skills = [
        "ioc-enrichment",
        "malware-triage",
        "chatops",
    ]
    for skill_name in expected_skills:
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Expected skill file missing: {skill_path}"


def test_atomic_runbooks_exist():
    """Verify all 5 atomic runbooks exist in skills/secops/runbooks/."""
    expected_runbooks = [
        "domain",
        "ip-address",
        "hash",
        "url",
        "user",
    ]
    for runbook in expected_runbooks:
        skill_path = SKILLS_DIR / "runbooks" / runbook / "SKILL.md"
        assert skill_path.exists(), f"Expected atomic runbook missing: {skill_path}"


def test_incident_playbooks_exist():
    """Verify all 4 incident response playbooks exist in skills/secops/playbooks/."""
    expected_playbooks = [
        "compromised-account",
        "ransomware-response",
        "phishing-response",
        "investigation-report",
    ]
    for playbook in expected_playbooks:
        skill_path = SKILLS_DIR / "playbooks" / playbook / "SKILL.md"
        assert skill_path.exists(), f"Expected incident playbook missing: {skill_path}"


def test_recursive_skill_discovery():
    """Verify recursive discovery finds root, imported, runbook, and playbook skills."""
    discovered = get_skill_md_files()
    assert SKILLS_DIR / "SKILL.md" in discovered
    for skill_name in ["ioc-enrichment", "malware-triage", "chatops"]:
        assert SKILLS_DIR / skill_name / "SKILL.md" in discovered
    for runbook in ["domain", "ip-address", "hash", "url", "user"]:
        assert SKILLS_DIR / "runbooks" / runbook / "SKILL.md" in discovered
    for playbook in [
        "compromised-account",
        "ransomware-response",
        "phishing-response",
        "investigation-report",
    ]:
        assert SKILLS_DIR / "playbooks" / playbook / "SKILL.md" in discovered


@pytest.mark.parametrize(
    "skill_file", get_skill_files(), ids=lambda p: str(p.relative_to(SKILLS_DIR))
)
def test_skill_tool_filter_validity(skill_file: Path):
    """Verify every tool declared in any skill's tool_filter belongs to known tools or valid names."""
    content = skill_file.read_text(encoding="utf-8")
    meta = parse_yaml_frontmatter(content)
    tools = meta.get("tool_filter", [])
    assert isinstance(tools, list), f"{skill_file} 'tool_filter' must be a list"
    assert len(tools) > 0, f"{skill_file} 'tool_filter' must contain at least one tool"
    for tool in tools:
        assert tool in VALID_SECOPS_TOOLS, (
            f"Invalid tool '{tool}' in {skill_file.relative_to(SKILLS_DIR)}. "
            f"Must belong to known Chronicle Remote MCP tools or valid tool names."
        )


@pytest.mark.parametrize(
    "skill_file", get_skill_md_files(), ids=lambda p: str(p.relative_to(SKILLS_DIR))
)
def test_skill_required_markdown_sections(skill_file: Path):
    """Verify all required markdown sections are present in each SKILL.md."""
    content = skill_file.read_text(encoding="utf-8")
    headings = [
        line.strip().lstrip("#").strip()
        for line in content.splitlines()
        if line.strip().startswith("#")
    ]
    for section in REQUIRED_MARKDOWN_SECTIONS:
        found = any(section.lower() in h.lower() for h in headings)
        assert found, (
            f"{skill_file.relative_to(SKILLS_DIR)} missing required markdown section: '{section}'. "
            f"Observed headings: {headings}"
        )


def test_get_secops_skill_tools_aggregate():
    """Verify get_secops_skill_tools() aggregates unique tools across all SecOps skills."""
    from gcp_agent.agent import get_secops_skill_tools

    tools = get_secops_skill_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0

    # Ensure uniqueness
    assert len(tools) == len(set(tools))

    # Verify key tools from core skill and sub-skills are present
    assert "list_rules" in tools
    assert "list_cases" in tools
    assert "summarize_entity" in tools
    assert "update_case" in tools
    assert "close_case" in tools
    assert "get_ioc_matches" in tools


def test_get_secops_skill_tools_by_name():
    """Verify get_secops_skill_tools(skill_name) returns tools for specific skills."""
    from gcp_agent.agent import get_secops_skill_tools

    chatops_tools = get_secops_skill_tools("chatops")
    assert chatops_tools == [
        "list_cases",
        "get_case",
        "update_case",
        "close_case",
        "add_case_comment",
    ]

    ioc_tools = get_secops_skill_tools("ioc-enrichment")
    assert ioc_tools == [
        "summarize_entity",
        "search_entity",
        "get_ioc_matches",
        "list_reference_lists",
    ]

    malware_tools = get_secops_skill_tools("malware-triage")
    assert "list_rules" in malware_tools
    assert "get_security_alert" in malware_tools

    # Test underscore to hyphen normalization
    malware_tools_norm = get_secops_skill_tools("malware_triage")
    assert malware_tools_norm == malware_tools

    # Test root skill
    root_tools = get_secops_skill_tools("gcp-secops-analyst")
    assert "list_rules" in root_tools
    assert "list_cases" in root_tools


def test_get_secops_skill_tools_unknown():
    """Verify unknown skill names return an empty list."""
    from gcp_agent.agent import get_secops_skill_tools

    tools = get_secops_skill_tools("non_existent_skill_name")
    assert tools == []


def test_get_secops_skill_tools_fallback_env(monkeypatch):
    """Verify get_secops_skill_tools falls back to MCP_TOOL_FILTER if no skills found."""
    from gcp_agent import agent

    monkeypatch.setattr(agent, "_get_skills_dir", lambda svc=None: None)
    monkeypatch.setenv("MCP_TOOL_FILTER", "custom_tool_1, custom_tool_2")

    tools = agent.get_secops_skill_tools()
    assert tools == ["custom_tool_1", "custom_tool_2"]


def test_load_instructions_secops():
    """Verify load_instructions('secops') indexes catalog and aggregates sub-skills."""
    from gcp_agent.agent import load_instructions

    instructions = load_instructions("secops")
    assert "# Google Cloud SecOps (Chronicle) Analyst Skill" in instructions
    assert "## Specialized Sub-Skills Catalog" in instructions
    assert "**chatops**" in instructions
    assert "**ioc-enrichment**" in instructions
    assert "**malware-triage**" in instructions
    assert "## Detailed Sub-Skill Runbooks" in instructions
    assert "### Sub-Skill: chatops" in instructions
    assert "### Sub-Skill: ioc-enrichment" in instructions
    assert "### Sub-Skill: malware-triage" in instructions


def test_load_instructions_recommender():
    """Verify load_instructions('recommender') loads single skill without catalog."""
    from gcp_agent.agent import load_instructions

    instructions = load_instructions("recommender")
    assert "# Google Cloud Recommender & FinOps Skill" in instructions
    assert "## Specialized Sub-Skills Catalog" not in instructions


def test_load_instructions_nonexistent():
    """Verify load_instructions falls back to default message when skill file is missing."""
    from gcp_agent.agent import load_instructions

    instructions = load_instructions("unknown_service_xyz")
    assert (
        "You are a helpful assistant with access to Google Cloud unknown_service_xyz tools."
        in instructions
    )


def test_tool_filter_initialization(monkeypatch):
    """Verify TOOL_FILTER initializes correctly based on env and service name."""
    import importlib
    from gcp_agent import agent

    # Case 1: Explicit MCP_TOOL_FILTER
    monkeypatch.setenv("MCP_TOOL_FILTER", "tool1, tool2")
    monkeypatch.setenv("ACTIVE_MCP_SERVICE", "secops")
    importlib.reload(agent)
    assert agent.TOOL_FILTER == ["tool1", "tool2"]

    # Case 2: No MCP_TOOL_FILTER, SERVICE_NAME == "secops"
    monkeypatch.delenv("MCP_TOOL_FILTER", raising=False)
    monkeypatch.setenv("ACTIVE_MCP_SERVICE", "secops")
    importlib.reload(agent)
    assert agent.TOOL_FILTER is not None
    assert "list_rules" in agent.TOOL_FILTER
    assert "list_cases" in agent.TOOL_FILTER
    assert "close_case" in agent.TOOL_FILTER

    # Case 3: No MCP_TOOL_FILTER, SERVICE_NAME == "recommender"
    monkeypatch.delenv("MCP_TOOL_FILTER", raising=False)
    monkeypatch.setenv("ACTIVE_MCP_SERVICE", "recommender")
    importlib.reload(agent)
    assert agent.TOOL_FILTER is None

    # Reset agent back to default environment
    monkeypatch.undo()
    importlib.reload(agent)
