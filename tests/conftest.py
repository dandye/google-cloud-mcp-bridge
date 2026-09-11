"""Pytest fixtures and test environment configuration."""

import pytest


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set default test environment variables."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("ACTIVE_MCP_SERVICE", "recommender")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
