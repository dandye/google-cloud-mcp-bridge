"""Basic unit test suite for google-cloud-mcp-bridge."""

from pathlib import Path

from typer.testing import CliRunner

from manage import app


runner = CliRunner()


def test_mcp_catalog():
    """Verify MCP catalog contains required Google Cloud remote MCP services."""
    from gcp_agent.agent import MCP_CATALOG

    expected_services = [
        "recommender",
        "compute",
        "bigquery",
        "cloudbilling",
        "run",
        "storage",
        "secops",
    ]
    for service in expected_services:
        assert service in MCP_CATALOG
        assert MCP_CATALOG[service].startswith("https://")


def test_skills_secops_exists():
    """Verify default skills/secops/SKILL.md documentation exists."""
    base_dir = Path(__file__).resolve().parent.parent
    skill_file = base_dir / "skills" / "secops" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "secops" in content.lower()


def test_skills_recommender_exists():
    """Verify default skills/recommender/SKILL.md documentation exists."""
    base_dir = Path(__file__).resolve().parent.parent
    skill_file = base_dir / "skills" / "recommender" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "recommender" in content.lower()


def test_cli_info_command():
    """Verify manage.py info command runs and outputs environment status."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Google Cloud MCP Bridge" in result.output
    assert "Active MCP Service" in result.output


def test_cli_help_command():
    """Verify manage.py --help lists commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "info" in result.output
    assert "chat" in result.output
    assert "client" in result.output
    assert "serve" in result.output
    assert "deploy" in result.output
