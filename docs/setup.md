# Setup & Installation - google-cloud-mcp-bridge

## Prerequisites

- Python >= 3.11
- `just` task runner (`cargo install just` or system package manager)
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `gcloud` CLI authenticated with Application Default Credentials (ADC)
- Google Cloud Project with billing enabled and required APIs:
  - `chronicle.googleapis.com` (for Google SecOps / Chronicle Remote MCP)
  - `recommender.googleapis.com` (for Recommender Remote MCP)
  - `aiplatform.googleapis.com` (for Vertex AI Agent Runtime / Reasoning Engine)
  - `agentregistry.googleapis.com` (for Google Cloud Agent Registry cataloging)
  - `discoveryengine.googleapis.com` (for Gemini Enterprise publication)

---

## IAM Roles & Permissions

Ensure your authenticated identity (or the runtime Service Account) possesses the necessary IAM roles:

| Component | IAM Role | Purpose |
| :--- | :--- | :--- |
| **Chronicle SIEM/SOAR** | `roles/chronicle.viewer` | Read alerts, detection rules, entities, and IOC matches |
| **Chronicle SOAR** | `roles/chronicle.editor` | Manage SOAR cases and append investigation comments |
| **Vertex AI** | `roles/aiplatform.user` | Deploy and query Reasoning Engine instances |
| **Agent Registry** | `roles/agentregistry.editor` | Catalog agent instances in Agent Registry |
| **Gemini Enterprise** | `roles/discoveryengine.editor` | Bind deployed agent to Gemini Enterprise chat apps |

Enable required APIs:
```bash
gcloud services enable \
  chronicle.googleapis.com \
  recommender.googleapis.com \
  aiplatform.googleapis.com \
  agentregistry.googleapis.com \
  discoveryengine.googleapis.com \
  --project="your-project-id"
```

---

## Quickstart

### 1. Environment Initialization
Run the initialization recipe to provision the virtual environment, install dependencies, and generate `.env` from template:
```bash
just setup
```

### 2. Configure Environment Variables
Edit `.env` to configure your target MCP service and project settings:
```bash
# Target MCP Service: 'secops' (default) or 'recommender'
ACTIVE_MCP_SERVICE="secops"

# Google Cloud Project & Region
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"

# LLM & Vertex AI Runtime
GOOGLE_GENAI_USE_VERTEXAI="true"
GEMINI_MODEL="gemini-2.5-flash"

# Optional: Restrict tool scoping to specific MCP tools (comma-separated)
# MCP_TOOL_FILTER="summarize_entity,search_entity,get_ioc_matches"
```

### 3. Authenticate Application Default Credentials
```bash
gcloud auth application-default login
```

### 4. Verify Remote MCP Tool Discovery
Verify that the ADK `McpToolset` successfully authenticates and discovers the remote MCP endpoints:
```bash
just client
```
When `ACTIVE_MCP_SERVICE="secops"`, this dynamically aggregates and validates tools across all skills in `skills/secops/`.

### 5. Run Interactive Conversational Prompts
Test conversational reasoning locally using the ADK Runner:
```bash
# SecOps threat investigation prompt:
just chat "Investigate domain evil-sample.com for active IOC matches and summarize findings."

# Or Recommender cost analysis prompt (when ACTIVE_MCP_SERVICE="recommender"):
just chat "What recommendations can you provide for persistent disks?"
```

---

## Local Development & Quality Gates

Run automated checks before submitting changes:

```bash
# Run unit tests across all skill definitions and agents
just unit-test

# Run linter and formatting checks (Ruff)
just lint

# Run typechecker (Mypy)
just typecheck

# Run live integration tests against deployed Vertex AI Reasoning Engine
just integration-test

# Launch local FastAPI server with Uvicorn on port 8080
just serve
```

---

## Cloud Deployment

Deploy the agent to Vertex AI Agent Runtime (Reasoning Engine) and automatically catalog in Google Cloud Agent Registry:
```bash
just deploy
```
This executes `scripts/deploy.sh`, which packages the environment, applies schema flattener bypass configurations, provisions the Reasoning Engine instance, and registers the deployment manifest.
