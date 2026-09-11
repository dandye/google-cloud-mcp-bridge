---
name: secops-skill-template
description: Standard template and specification for Google Cloud SecOps skills and atomic runbooks.
role: SOC Analyst
category: SecurityOperations
tool_filter:
  - summarize_entity
  - search_entity
inputs:
  - name: target_identifier
    type: string
    description: Entity, indicator, alert ID, or query parameter under investigation.
    required: true
  - name: time_window
    type: string
    description: Investigation time window (e.g., last 24 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious, Inconclusive).
  - name: findings_summary
    type: string
    description: Synthesized analysis including internal sightings and threat context.
  - name: recommended_actions
    type: array
    description: Ordered remediation, containment, or escalation actions.
---

# SecOps Skill Template & Specification

This template defines the mandatory structure and schema for all security operations skills within skills/secops/.

## 1. Overview & Objective
Briefly describe the security domain, investigative objective, and trigger criteria for this skill. Explain what problem this skill solves and what telemetry sources it accesses.

## 2. Remote MCP Tool Scope
Explicitly enumerate the subset of Google Cloud SecOps (Chronicle) Remote MCP tools required by this skill. Only include tools that are strictly necessary to avoid context bloat and schema processing overhead.

- tool_name_1: Purpose of this tool in the workflow.
- tool_name_2: Purpose of this tool in the workflow.

## 3. Step-by-Step Reasoning Protocol
Provide an ordered sequence of reasoning steps the agent must execute:

1. **Input Normalization & Validation**:
   - Parse and validate inputs (defang/refang URLs, sanitize IP formats, normalize hashes).
   - Verify required tenant parameters (project_id, customer_id, region).

2. **Telemetry Sighting & External Lookups**:
   - Perform internal SIEM checks using scoped MCP tools.
   - Cross-reference external threat intelligence signals.

3. **Contextual Correlation**:
   - Correlate events across hosts, users, and network connections.
   - Establish baseline normality and detect deviations.

4. **Synthesis & Verdict Formulation**:
   - Weigh evidence to assign a confidence-weighted verdict (Benign, Suspicious, Malicious).
   - Highlight potential false positives or unobserved blind spots.

## 4. Human-in-the-Loop (HITL) Safeguards
Define state-changing boundaries and actions requiring explicit human approval:
- Actions that may be performed autonomously (e.g., read-only queries, comment creation, entity lookups).
- Actions requiring human authorization (e.g., host isolation, credential revocation, rule deletion).

## 5. Example Prompts
Provide at least two realistic analyst prompts that should activate this skill:
- "Analyze the suspicious domain evil-login-portal[.]com observed in outbound proxy logs over the last 6 hours."
- "Check if hash 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f has been seen on any corporate endpoints."

## 6. Output Schema & Reporting Structure
Specify the format for the final output delivered to the analyst or supervisor:
- **Executive Summary**: 2-3 sentence overview of findings.
- **Key Indicators**: Table of observed entities, types, and threat scores.
- **Chronological Timeline**: Sequence of events with UTC timestamps.
- **Recommended Next Steps**: Prioritized containment and remediation steps.
