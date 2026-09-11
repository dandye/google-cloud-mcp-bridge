---
name: chatops
description: >
  Facilitates human-in-the-loop collaboration, structured security notifications,
  action approvals for containment, and case collaboration in Google Cloud SecOps.
role: Incident Commander & Collaboration Agent
category: Collaboration
tool_filter:
  - list_cases
  - get_case
  - update_case
  - close_case
  - add_case_comment
inputs:
  - name: incident_context
    type: string
    description: Incident summary, affected assets, severity, or case ID.
    required: true
  - name: proposed_action
    type: string
    description: State-changing action requiring approval or notification.
    required: false
outputs:
  - name: notification_card
    type: string
    description: Formatted message or card layout for human analyst communication.
  - name: case_update_status
    type: string
    description: Confirmation of case comments or status updates logged in Chronicle.
---

# ChatOps & Human-in-the-Loop Collaboration Skill

This skill governs how autonomous security agents communicate with human security analysts, request authorization for disruptive actions, and synchronize incident updates into Google Cloud SecOps (Chronicle) cases.

## 1. Overview & Objective
Security operations requires human-in-the-loop (HITL) oversight for high-stakes remediation. This skill ensures:
1. High-severity incidents are immediately escalated with concise, decision-ready briefings.
2. Destructive or state-changing actions (host isolation, credential revocation, rule modifications) require explicit human confirmation.
3. Case timelines in Chronicle SOAR are automatically updated with investigation notes, evidence, and approvals.

## 2. Remote MCP Tool Scope
This skill utilizes Chronicle case management and collaboration tools:
- `list_cases`: Finds active cases associated with an alert, entity, or incident.
- `get_case`: Retrieves case priority, current status, assignees, and existing notes.
- `update_case`: Modifies case severity, status (e.g., In Progress, Escalated), or priority.
- `close_case`: Finalizes and closes a case once remediation is verified.
- `add_case_comment`: Appends structured investigation findings and analyst decisions to the case audit log.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Incident Assessment & Context Gathering
- Determine current case priority, assigned responders, and existing investigative notes using `get_case`.
- Review associated alerts and impacted assets to establish severity and scope.

### Step 2: Structured Analyst Notifications
Format analyst alerts using a clean, standardized layout:
- **Title**: `[SEVERITY] <Incident Title>` (e.g., `[HIGH] Honeytoken Credential Access on service-account-prod`)
- **Key Details**:
  - **Timestamp (UTC)**: Incident detection time.
  - **Target Entity**: Hostname, IP, or User ID.
  - **Confidence**: High / Medium / Low based on multi-source correlation.
- **Evidence Summary**: 2-3 bullet points citing detection rules or telemetry.
- **Action Buttons / Proposals**: Clear options presented for analyst decision.

### Step 3: Chronicle Case Audit Logging
- When an analyst makes a decision or new evidence is discovered:
  - Call `add_case_comment` with a Markdown-formatted entry summarizing findings.
  - If closing an investigation, ensure all root causes and containment actions are recorded in the case before invoking `close_case`.

## 4. Human-in-the-Loop (HITL) Safeguards
Before executing any irreversible or high-risk action:
- **Never execute autonomously**:
  - Isolating or shutting down a production host.
  - Disabling or locking user or service accounts.
  - Blocking egress routes or applying firewall modifications.
  - Closing a major security incident case.
- **Propose to Human**:
  - State the proposed action clearly.
  - Present the supporting evidence (verdict, affected assets, threat intelligence signals).
  - Explicitly ask for human approval before proceeding.

## 5. Example Prompts
- *"Draft an incident notification for the SOC channel regarding critical alert 99120."*
- *"Add our investigation findings for suspicious IP 198.51.100.45 to Chronicle case CASE-4021."*
- *"Request human confirmation before isolating host db-cluster-worker-02."*

## 6. Output Schema
Deliver a structured ChatOps briefing:
- **Header**: `### Incident Escalation: <Title>`
- **Severity Badge**: `[CRITICAL | HIGH | MEDIUM | LOW]`
- **Incident Summary**: Concise summary of what occurred.
- **Impacted Scope**: Systems and identities affected.
- **Proposed Action (Requires Human Approval)**: Action description and potential operational impact.
- **Case Audit Log**: Confirmation of notes logged to Chronicle SOAR.
