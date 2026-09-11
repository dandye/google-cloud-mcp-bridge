"""Unit tests for SecOps skill definitions and YAML metadata validation."""

from pathlib import Path
import pytest
import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills" / "secops"


def get_skill_files():
    """Retrieve all SKILL.md and template files under skills/secops/."""
    files = list(SKILLS_DIR.glob("**/SKILL.md"))
    template = SKILLS_DIR / "TEMPLATE.md"
    if template.exists():
        files.append(template)
    return files


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
