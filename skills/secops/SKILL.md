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

## 1. Overview & Objective
Investigates security events, searches Chronicle UDM logs, analyzes alerts, and inspects security cases using Google Cloud Security Operations (SecOps) remote MCP tools. This skill serves as the primary orchestrator for SecOps investigations across the enterprise environment.

## 2. Remote MCP Tool Scope

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

## 3. Step-by-Step Reasoning Protocol

1. **Scope and Customer Context**:
   - Ensure the query identifies the target project, customer ID, or time range (defaulting to the last 24-48 hours if unspecified).
2. **Triaging Alerts**:
   - Call `list_security_alerts` or `get_security_alert` first to understand the triggered rule and involved assets/users.
3. **Correlating Telemetry**:
   - Use `udm_search` to verify whether suspicious activity preceded or followed the alert.
   - Use `summarize_entity` to establish baseline behavior for the affected user or asset.
4. **Actionable Findings**:
   - Summarize the attack timeline, involved entities, IOCs, and recommended containment steps.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only telemetry queries, UDM log searches, alert details retrieval, and entity summarization.
- **Actions Requiring Human Authorization**: Any state-changing containment action, including host isolation, account revocation, perimeter block rules, or closing security cases.

## 5. Example Prompts
- "Search Chronicle UDM logs for failed login attempts against user admin@example.com over the last 24 hours."
- "Investigate recent high-severity alerts in Chronicle and summarize affected assets and users."
- "Check if indicator 198.51.100.25 has been seen in our environment and summarize its entity reputation."

## 6. Output Schema & Reporting Structure
Deliver a structured analysis report:
- **Executive Summary**: High-level overview of findings and overall risk verdict.
- **Involved Entities**: List of affected IP addresses, hostnames, user accounts, and hashes.
- **Chronological Timeline**: Sequence of observed security events with UTC timestamps.
- **Recommended Actions**: Containment, eradication, and post-incident verification steps with HITL authorization flags.
