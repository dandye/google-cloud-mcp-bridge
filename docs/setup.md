# Setup & Installation - google-cloud-mcp-bridge

## Prerequisites

- Python >= 3.11
- `just` task runner (`cargo install just` or system package manager)
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `gcloud` CLI authenticated with Application Default Credentials (ADC)
- Active Google Cloud project with required APIs enabled:
  - `recommender.googleapis.com` (or other target MCP service)
  - `aiplatform.googleapis.com` (for Vertex AI)

## Quick Start

1. Initialize environment and dependencies:
   ```bash
   just setup
   ```
   This creates `.env` from `.env.example`, provisions a virtual environment in `.venv`, and installs dependencies via `uv`.

2. Authenticate Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```

3. Update `.env` with your Google Cloud settings:
   ```bash
   GOOGLE_CLOUD_PROJECT="your-project-id"
   GOOGLE_CLOUD_LOCATION="us-central1"
   ACTIVE_MCP_SERVICE="recommender"
   ```

4. Verify connection to the remote MCP server:
   ```bash
   just client
   ```

5. Run test chat prompt:
   ```bash
   just chat "Hello! What tools do you have available?"
   ```

6. Run test suite:
   ```bash
   just test
   ```
