---
name: gcp-secops-analyst
description: >
  Investigates security events, searches Chronicle UDM logs, analyzes alerts,
  and inspects security cases using the Google Cloud Security Operations (SecOps)
  remote MCP server. Use when users ask to search UDM logs, investigate IOCs,
  review detections, check cases, or analyze alerts.
role: Lead SOC Analyst & Orchestrator
category: SecurityOperations
tool_filter:
  - list_rules
  - get_rule
  - get_rule_detections
  - list_security_alerts
  - get_security_alert
  - summarize_entity
  - search_entity
  - get_ioc_matches
  - list_cases
  - get_case
  - add_case_comment
  - list_reference_lists
---

# Google Cloud SecOps (Chronicle) Analyst Skill

This skill instructs the agent on how to use the Google Cloud Security Operations (SecOps / Chronicle) remote MCP server tools (`https://us-chronicle.googleapis.com/mcp`) for security triage, UDM searches, alert analysis, and incident investigations.

## Key Tools from Remote MCP Server

### 1. Unified Data Model (UDM) & Log Search
- `udm_search`: Executes a UDM search query across Chronicle logs.
  - Formulate valid UDM filter expressions (e.g. `metadata.event_type = "USER_LOGIN" AND target.user.userid = "..."`).
- `translate_udm_query`: Translates natural language questions into UDM search query syntax.
- `search_raw_logs`: Searches unparsed raw logs when UDM schema fields are not available.

### 2. Security Alerts & Investigations
- `list_security_alerts`: Lists active alerts matching time windows, severity, or rule filters.
- `get_security_alert`: Retrieves detailed context, events, and telemetry for a specific alert ID.
- `trigger_investigation`: Initiates an automated investigation workflow on an alert or entity.
- `get_alert_latest_investigation`: Fetches investigation status and findings.

### 3. Entity Summarization & Threat Indicators
- `summarize_entity`: Provides a risk summary and behavioral timeline for an entity (IP, domain, hostname, user).
- `search_entity`: Searches the entity graph by identifier.
- `get_ioc_match`: Checks if specific IOCs (hashes, IPs, domains) have matched in the environment.

### 4. Case Management & Collaboration
- `list_cases`: Lists open security cases and incidents.
- `get_case`: Fetches complete case details, priority, and assigned analysts.
- `create_case_comment`: Posts investigation notes and evidence into a case.

---

## Workflow Guidelines

1. **Scope and Customer Context**:
   - Ensure the query identifies the target project, customer ID, or time range (defaulting to the last 24-48 hours if unspecified).
2. **Triaging Alerts**:
   - Call `list_security_alerts` or `get_security_alert` first to understand the triggered rule and involved assets/users.
3. **Correlating Telemetry**:
   - Use `udm_search` to verify whether suspicious activity preceded or followed the alert.
   - Use `summarize_entity` to establish baseline behavior for the affected user or asset.
4. **Actionable Findings**:
   - Summarize the attack timeline, involved entities, IOCs, and recommended containment steps.
