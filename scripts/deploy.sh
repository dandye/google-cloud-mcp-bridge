#!/usr/bin/env bash
# ==============================================================================
# Deployment Script: Google Cloud Remote MCP Bridge on Agent Runtime
# ==============================================================================
# This script automates:
# 1. Verification of environment variables and CLI tools (gcloud, agents-cli).
# 2. Enabling required Google Cloud APIs for Agent Runtime & Agent Registry.
# 3. Creating a dedicated Service Account with least-privilege IAM roles.
# 4. Deploying the ADK agent to Agent Runtime using agents-cli.
# 5. Verifying automatic cataloging in Google Cloud Agent Registry.
# 6. Publishing the agent to Gemini Enterprise via agents-cli.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

# ------------------------------------------------------------------------------
# 1. Configuration & Parameter Validation
# ------------------------------------------------------------------------------
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-${GCP_PROJECT_ID:-}}"
REGION="${GOOGLE_CLOUD_REGION:-${GCP_REGION:-us-central1}}"
ACTIVE_MCP_SERVICE="${ACTIVE_MCP_SERVICE:-secops}"
SERVICE_NAME="${SERVICE_NAME:-gcp-${ACTIVE_MCP_SERVICE}-agent}"
SA_NAME="${SA_NAME:-chronicle-mcp-sa}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: Google Cloud Project ID is not set."
  echo "Please export GOOGLE_CLOUD_PROJECT='your-project-id' and re-run."
  exit 1
fi

echo "=================================================================="
echo " Starting Agent Runtime Deployment: $SERVICE_NAME"
echo " Project ID : $PROJECT_ID | Region: $REGION | Service: $ACTIVE_MCP_SERVICE"
echo "=================================================================="

# Check CLI prerequisites
if ! command -v agents-cli &>/dev/null; then
  echo "ERROR: 'agents-cli' is not installed."
  echo "Install it via: uv tool install google-agents-cli"
  exit 1
fi

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# ------------------------------------------------------------------------------
# 2. Enable Required Google Cloud APIs
# ------------------------------------------------------------------------------
echo ""
echo "--> Step 1: Enabling required Google Cloud APIs..."
REQUIRED_APIS=(
  "aiplatform.googleapis.com"
  "agentregistry.googleapis.com"
  "discoveryengine.googleapis.com"
)
if [[ "$ACTIVE_MCP_SERVICE" == "secops" ]]; then
  REQUIRED_APIS+=("chronicle.googleapis.com")
else
  REQUIRED_APIS+=("recommender.googleapis.com")
fi

gcloud services enable "${REQUIRED_APIS[@]}" --project="$PROJECT_ID"

echo "    [OK] APIs enabled successfully."

# ------------------------------------------------------------------------------
# 3. Create Dedicated Service Account & Grant IAM Roles
# ------------------------------------------------------------------------------
echo ""
echo "--> Step 2: Configuring Service Account and IAM Roles..."

if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
  gcloud iam service-accounts create "$SA_NAME" \
    --display-name="MCP Bridge Agent Runtime SA" \
    --project="$PROJECT_ID"
  echo "    Created service account: $SA_EMAIL"
else
  echo "    Service account already exists: $SA_EMAIL"
fi

# 1. roles/mcp.toolUser: Required to execute tool calls on Google Remote MCP servers
echo "    Granting roles/mcp.toolUser..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/mcp.toolUser" \
  --condition=None \
  --quiet

# 2. Service-specific viewer roles
if [[ "$ACTIVE_MCP_SERVICE" == "secops" ]]; then
  echo "    Granting roles/chronicle.viewer..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/chronicle.viewer" \
    --condition=None \
    --quiet
else
  echo "    Granting roles/recommender.viewer..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/recommender.viewer" \
    --condition=None \
    --quiet

  echo "    Granting roles/compute.viewer..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/compute.viewer" \
    --condition=None \
    --quiet
fi

# 3. roles/aiplatform.user: Required for the agent to call Vertex AI / Gemini models
echo "    Granting roles/aiplatform.user..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" \
  --condition=None \
  --quiet

echo "    [OK] IAM roles granted."

# ------------------------------------------------------------------------------
# 4. Deploy to Agent Runtime
# ------------------------------------------------------------------------------
echo ""
echo "--> Step 3: Deploying ADK Agent to Agent Runtime..."

ENV_VARS="ACTIVE_MCP_SERVICE=${ACTIVE_MCP_SERVICE},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=${REGION},ADK_DISABLE_JSON_SCHEMA_FOR_FUNC_DECL=true"
if [[ "$ACTIVE_MCP_SERVICE" == "secops" ]]; then
  ENV_VARS="${ENV_VARS},SECOPS_MCP_URL=${SECOPS_MCP_URL:-https://us-chronicle.googleapis.com/mcp}"
fi

agents-cli deploy \
  --deployment-target="agent_runtime" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --service-name="$SERVICE_NAME" \
  --service-account="$SA_EMAIL" \
  --update-env-vars="$ENV_VARS" \
  --no-confirm-project

echo "    [OK] Deployed successfully to Agent Runtime."


# ------------------------------------------------------------------------------
# 5. Verify Cataloging in Google Cloud Agent Registry
# ------------------------------------------------------------------------------
echo ""
echo "--> Step 4: Verifying registration in Google Cloud Agent Registry..."

gcloud alpha agent-registry agents list \
  --project="$PROJECT_ID" \
  --location="$REGION" \
  --format="table(displayName,name,createTime)" || true

echo "    [OK] Agent Runtime agents are automatically cataloged in Agent Registry."

# ------------------------------------------------------------------------------
# 6. Publish to Gemini Enterprise App
# ------------------------------------------------------------------------------
echo ""
echo "--> Step 5: Publishing to Gemini Enterprise App..."

if [[ -n "${GEMINI_ENTERPRISE_APP_ID:-}" ]]; then
  echo "    Publishing agent to: $GEMINI_ENTERPRISE_APP_ID"
  if [[ "$ACTIVE_MCP_SERVICE" == "secops" ]]; then
    AGENT_DISPLAY_NAME="Google SecOps Agent"
    AGENT_DESC="Autonomous security operations assistant powered by Chronicle Remote MCP, providing IOC enrichment, malware triage, atomic investigation runbooks, and incident response playbooks."
    AGENT_TOOL_DESC="Investigates IOCs, domains, hashes, IPs, and users, triages alerts, queries Chronicle UDM events, and manages security cases."
  else
    AGENT_DISPLAY_NAME="GCP Recommender Agent"
    AGENT_DESC="Audits Google Cloud resources and discovers cost optimization recommendations using Google's remote MCP server."
    AGENT_TOOL_DESC="Audits Google Cloud resources for idle persistent disks, underutilized VMs, and cost savings."
  fi

  # Gemini Enterprise publishing requires an active end-user seat license.
  # If GOOGLE_APPLICATION_CREDENTIALS is set to a service account (e.g. via direnv),
  # unsetting it allows agents-cli to authenticate with user credentials.
  PUBLISH_CMD=(env -u GOOGLE_APPLICATION_CREDENTIALS agents-cli publish gemini-enterprise \
    --gemini-enterprise-app-id="$GEMINI_ENTERPRISE_APP_ID" \
    --display-name="$AGENT_DISPLAY_NAME" \
    --description="$AGENT_DESC" \
    --tool-description="$AGENT_TOOL_DESC" \
    --deployment-target="agent_runtime" \
    --registration-type="adk")

  if [[ -n "${GEMINI_ENTERPRISE_AUTH_ID:-}" ]]; then
    PUBLISH_CMD+=(--authorization-id="$GEMINI_ENTERPRISE_AUTH_ID")
  fi

  "${PUBLISH_CMD[@]}"

  echo "    [OK] Successfully published to Gemini Enterprise!"
else
  echo "    NOTE: GEMINI_ENTERPRISE_APP_ID was not specified."
  echo "    To discover your Gemini Enterprise apps, run:"
  echo "      agents-cli publish gemini-enterprise --list"
  echo ""
  echo "    To publish interactively:"
  echo "      agents-cli publish gemini-enterprise --interactive"
  echo ""
  echo "    Or publish directly with the app ID:"
  echo "      agents-cli publish gemini-enterprise \\"
  echo "        --gemini-enterprise-app-id=\"projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/YOUR_APP_ID\" \\"
  echo "        --display-name=\"GCP Recommender Agent\" \\"
  echo "        --deployment-target=\"agent_runtime\" \\"
  echo "        --registration-type=\"adk\""
fi

echo ""
echo "=================================================================="
echo " Deployment and Governance Setup Complete!"
echo " Deployment Target: Agent Runtime ($REGION)"
echo " Governance Target: Google Cloud Agent Registry"
echo "=================================================================="
