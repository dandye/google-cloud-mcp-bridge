# GEMINI.md

This file provides guidance to Gemini Code Assist and AI pair programmers working in this repository.

## Code Style and Communication

**CRITICAL: Never use emojis. Anywhere. Ever.**
- No emojis in code comments
- No emojis in commit messages
- No emojis in pull request descriptions
- No emojis in code review comments
- No emojis in documentation
- Emojis are unprofessional and must not be used in any context

## Shell and Environment Variables

- In code and shell examples, define environment variables first (e.g. `PROJECT_ID="..."`) and then reference them as `$PROJECT_ID`.

## Git Worktree and Path Conventions

- This repository adheres to the `google-cloud-mcp-bridge__worktrees/` convention.
- Primary clone with `.git/` is located at `google-cloud-mcp-bridge__worktrees/main`.
- Linked worktrees exist as sibling folders (e.g., `google-cloud-mcp-bridge__worktrees/<branch_name>`).
- Always resolve internal paths relative to `BASE_DIR = Path(__file__).resolve().parent` to maintain portability across sibling worktrees.
- If removing a worktree containing git submodules under `external/`, deinitialize submodules first: `git submodule deinit --all -f` before removing the worktree.

## Architecture Overview

`google-cloud-mcp-bridge` connects the Google Agent Development Kit (ADK) directly to official Google Cloud Remote Model Context Protocol (MCP) Server endpoints (such as `recommender.googleapis.com/mcp`, `compute.googleapis.com/mcp`, `bigquery.googleapis.com/mcp`) using ADK's native `McpToolset`.

- `gcp_agent/agent.py`: Core ADK agent and FastAPI application exposing `/run` and `/stream` endpoints.
- `skills/recommender/SKILL.md`: ADK skill instructions guiding the agent when querying Google Cloud Recommender.
- `test_chat.py`: Local CLI runner using `InMemorySessionService` to test agent conversational prompts.
- `test_client.py`: Verifies `McpToolset` endpoint connectivity and tool discovery.
- `agents-cli-manifest.yaml`: Manifest for packaging and deploying to Google Cloud Agent Runtime.
- `deploy.sh`: Shell script orchestrating Cloud Run / Agent Runtime deployment and Gemini Enterprise publication.
- `manage.py`: Unified Typer CLI for local execution, diagnostics, server hosting, and deployment.

## Common Commands

| Task | Command | Description |
| :--- | :--- | :--- |
| **Setup** | `just setup` | Create virtualenv, copy `.env.example` to `.env`, and install dependencies |
| **Install** | `just install` | Install editable package and dev dependencies via uv |
| **Run Tests** | `just test` | Run pytest suite |
| **Coverage** | `just test-cov` | Run tests with terminal and HTML coverage report |
| **Lint** | `just lint` | Run ruff check and format inspection |
| **Format** | `just format` | Automatically fix and format code with ruff |
| **Typecheck** | `just typecheck` | Run mypy type analysis |
| **CLI Info** | `python manage.py info` | Print environment status via Typer CLI |
| **Test MCP Tools** | `just client` | Connect to active Google Cloud MCP endpoint and list tools |
| **Test Chat** | `just chat "prompt"` | Run conversational query through the ADK agent |
| **Start Server** | `just serve` | Launch local FastAPI agent server on port 8080 |
| **Deploy** | `just deploy` | Deploy to Google Cloud Agent Runtime via `deploy.sh` |
| **Clean** | `just clean` | Remove cache files, coverage reports, and build artifacts |
