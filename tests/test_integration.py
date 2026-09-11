"""Integration test suite for deployed Vertex AI Agent Runtime SecOps agent."""

import os
from typing import Any
import pytest
import requests
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest

DEFAULT_REASONING_ENGINE_ID = "3330461952219545600"
DEFAULT_PROJECT_NUMBER = "1002894625780"
DEFAULT_LOCATION = "us-central1"


@pytest.fixture(scope="module")
def auth_headers():
    """Retrieve fresh Google Cloud OAuth2 Bearer token."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())
    return {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="module")
def agent_endpoint():
    """Build the Reasoning Engine :query endpoint URL."""
    project_number = os.getenv("PROJECT_NUMBER", DEFAULT_PROJECT_NUMBER)
    location = os.getenv("GOOGLE_CLOUD_LOCATION", DEFAULT_LOCATION)
    engine_id = os.getenv("REASONING_ENGINE_ID", DEFAULT_REASONING_ENGINE_ID)
    return f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_number}/locations/{location}/reasoningEngines/{engine_id}:query"


@pytest.mark.integration
def test_agent_engine_capabilities_query(auth_headers, agent_endpoint):
    """Verify deployed Agent Engine responds to a capabilities query."""
    payload: dict[str, Any] = {
        "class_method": "query",
        "input": {
            "message": "Hello, briefly list the SecOps tools and capabilities available to you."
        },
    }
    response = requests.post(
        agent_endpoint, json=payload, headers=auth_headers, timeout=90
    )
    assert response.status_code == 200
    data = response.json()
    output = data.get("output", "")
    assert isinstance(output, str)
    assert len(output) > 50
    assert any(
        term in output.lower()
        for term in ["secops", "chronicle", "udm", "alert", "rule"]
    )


@pytest.mark.integration
def test_agent_engine_live_rule_listing(auth_headers, agent_endpoint):
    """Verify deployed Agent Engine executes list_rules via Remote MCP."""
    prompt = (
        "Please list the detection rules configured in Chronicle SIEM for "
        "project: dandye-0324-chronicle, customer ID: 7e977ce4-f45d-43b2-aea0-52f8b66acd80, region: us. "
        "Show up to 3 rules."
    )
    payload: dict[str, Any] = {
        "class_method": "query",
        "input": {"message": prompt},
    }
    response = requests.post(
        agent_endpoint, json=payload, headers=auth_headers, timeout=90
    )
    assert response.status_code == 200
    data = response.json()
    output = data.get("output", "")
    assert isinstance(output, str)
    assert "honeytoken" in output.lower() or "rule" in output.lower()
