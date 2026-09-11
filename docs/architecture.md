# Architecture Overview - google-cloud-mcp-bridge

## System Overview

`google-cloud-mcp-bridge` provides a direct bridge between the Google Agent Development Kit (ADK) and Google Cloud Remote Model Context Protocol (MCP) Server endpoints without requiring custom JSON-RPC transport code.

```text
User / App Prompt
       │
       ▼
 ┌───────────────┐
 │   ADK Agent   │  (FastAPI server / CLI runner)
 └───────┬───────┘
         │
         ▼  (Native ADK McpToolset)
 ┌───────────────┐
 │  Streamable   │  (StreamableHTTPConnectionParams + GoogleAuthRequest)
 │  HTTP Client  │
 └───────┬───────┘
         │
         ▼  (Google OAuth2 / ADC Bearer Token)
 ┌─────────────────────────────────────────────────────────────┐
 │  Google Cloud Remote MCP Server Endpoints                   │
 │                                                             │
 │  - recommender: https://recommender.googleapis.com/mcp     │
 │  - compute:     https://compute.googleapis.com/mcp         │
 │  - bigquery:    https://bigquery.googleapis.com/mcp        │
 │  - billing:     https://cloudbilling.googleapis.com/mcp    │
 │  - run:         https://run.googleapis.com/mcp             │
 │  - storage:     https://storage.googleapis.com/storage/mcp │
 └─────────────────────────────────────────────────────────────┘
```

## Component Boundaries

- `gcp_agent/agent.py`:
  - Instantiates `StreamableHTTPConnectionParams` with the target MCP endpoint and OAuth bearer tokens.
  - Registers the remote MCP tools via ADK's `McpToolset`.
  - Configures the ADK `Agent` with system instructions and domain skills.
  - Implements a FastAPI web server with streaming and JSON response endpoints.
- `skills/`:
  - Modular skill definitions (e.g., `skills/recommender/SKILL.md`) that guide agent reasoning when querying specific Google Cloud MCP tools.
- `manage.py`:
  - Unified operational CLI for local execution, connection verification, server launching, and deployment.
- `deploy.sh` & `agents-cli-manifest.yaml`:
  - Automation scripts for containerizing and deploying to Google Cloud Agent Runtime, with optional registration in Google Cloud Agent Registry and Gemini Enterprise.
- `external/`:
  - Git submodules container for linked MCP servers, helper libraries, or test suites.
- `scripts/`:
  - Environment provisioning and maintenance scripts.
- `tests/`:
  - Pytest unit and integration test suite.
