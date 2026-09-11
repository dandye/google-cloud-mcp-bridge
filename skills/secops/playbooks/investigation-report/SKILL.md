---
name: playbook-investigation-report
description: >
  Generate standardized security investigation reports, shift handoff summaries,
  executive incident briefs, and Chronicle SOAR case audit records.
role: Lead SOC Analyst & Technical Writer
category: Reporting
tool_filter:
  - list_cases
  - get_case
  - add_case_comment
  - summarize_entity
  - search_entity
  - list_security_alerts
inputs:
  - name: case_id
    type: string
    description: Chronicle SOAR case ID or incident identifier to report on.
    required: true
  - name: report_type
    type: string
    description: Report format (Executive Summary, Technical Case Report, Shift Handoff, Post-Incident Review).
    required: false
outputs:
  - name: report_markdown
    type: string
    description: Comprehensive Markdown formatted report ready for stakeholder delivery.
  - name: audit_status
    type: string
    description: Status of report documentation logged to Chronicle SOAR case audit trail.
---

# Security Investigation & Shift Reporting Playbook

This playbook defines structured workflows for consolidating security investigation findings into high-impact reports for technical teams, executive stakeholders, shift handoffs, and Chronicle SOAR audit logs.

## 1. Overview & Objective
Clear documentation is essential for incident closure, compliance, and continuous improvement. This playbook coordinates:
1. Retrieval and aggregation of all telemetry, alert details, and analyst notes from Chronicle cases.
2. Synthesis of a cohesive investigation narrative with root cause attribution.
3. Generation of role-appropriate briefings (Executive Brief, Technical Deep Dive, Shift Handoff).
4. Permanent recording of the finalized report into Chronicle case comments.

## 2. Remote MCP Tool Scope
- `list_cases`: Locates relevant cases by date, priority, or entity.
- `get_case`: Pulls comprehensive case metadata, priority, stage, assigned analysts, and comment history.
- `add_case_comment`: Posts the finalized report into the Chronicle SOAR case audit log.
- `summarize_entity`: Enriches key entities cited in the report with threat intelligence context.
- `search_entity`: Gathers related assets and identities for complete scope documentation.
- `list_security_alerts`: Summarizes all alerts tied to the case for timeline construction.

## 3. Step-by-Step Reasoning Protocol

### Phase 1: Case Context & Evidence Ingestion
- Call `get_case` with `case_id` to retrieve:
  - Case title, severity level, creation time, and current status.
  - Full comment history and analyst investigative findings.
  - Attached alert IDs and entity graph associations.

### Phase 2: Timeline Reconstruction
- Call `list_security_alerts` for the case to extract UTC timestamps of:
  - Initial alert trigger.
  - First observed adversary action.
  - Analyst initial triage response.
  - Containment execution.
- Build an ordered chronological timeline table.

### Phase 3: Technical Synthesis & Root Cause Analysis
- Correlate key entities with `summarize_entity`:
  - Identify initial access vector (e.g., Phishing, Exploitation, Stolen Credentials).
  - Trace lateral movement and persistence techniques mapped to MITRE ATT&CK.
  - State the definitive root cause or note gaps where telemetry is inconclusive.

### Phase 4: Report Structuring by Audience
Format the report based on requested `report_type`:
- **Executive Summary**: 1-page high-level brief for leadership (business impact, status, key takeaways).
- **Technical Case Report**: Detailed forensic breakdown with full IOC tables and command lines.
- **Shift Handoff Summary**: Current active status, pending action items, and open questions for the incoming shift.
- **Post-Incident Review (PIR)**: Lessons learned, detection rule gaps, and architectural recommendations.

### Phase 5: SOAR Case Documentation
- Call `add_case_comment` to persist the finalized report into the Chronicle SOAR case record.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous**: Gathering case details, compiling timelines, drafting reports, and posting case comments.
- **Approval Required**: External delivery of reports to non-security stakeholders or public disclosure requires human analyst approval.

## 5. Example Prompts
- *"Generate a technical investigation report for Chronicle case CASE-1092 and attach it to the case."*
- *"Compile a shift handoff report summarizing all high-severity incidents worked over the last 12 hours."*
- *"Draft an executive summary brief for the ransomware incident investigated on tenant 7e977ce4-f45d-43b2-aea0-52f8b66acd80."*

## 6. Output Schema
Deliver a structured Markdown report:
- **Title**: `# Security Incident Investigation Report: [Case ID] - [Incident Title]`
- **Executive Summary**: 2-3 paragraph overview of what occurred and current resolution.
- **Incident Metadata**: Severity, Time Detected, Time Contained, Lead Analyst.
- **Attack Timeline**: Markdown table of timestamps and milestones.
- **Key Entities & IOCs**: Table of observed hashes, IPs, domains, and accounts.
- **Root Cause & Attack Vector**: Detailed narrative with MITRE ATT&CK technique IDs.
- **Remediation & Lessons Learned**: Actionable post-incident hardening recommendations.
