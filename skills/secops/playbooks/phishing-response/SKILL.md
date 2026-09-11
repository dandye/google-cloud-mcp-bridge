---
name: playbook-phishing-response
description: >
  Investigate user-reported phishing emails, suspicious credential harvest portals,
  malicious attachments, and internal email recipient exposure.
role: SOC Analyst & Phishing Triage Specialist
category: IncidentResponse
tool_filter:
  - summarize_entity
  - search_entity
  - get_ioc_matches
  - list_security_alerts
  - get_security_alert
  - list_cases
  - get_case
  - add_case_comment
inputs:
  - name: reported_indicator
    type: string
    description: Phishing URL, sender domain, sender IP, or suspect attachment hash.
    required: true
  - name: target_recipient
    type: string
    description: Email address of user who received the suspicious communication.
    required: false
  - name: case_id
    type: string
    description: Chronicle SOAR case ID.
    required: false
outputs:
  - name: phishing_verdict
    type: string
    description: Classification (Malicious Phish, Credential Harvester, Benign Spam, Legitimate).
  - name: exposed_users
    type: array
    description: List of internal users who received or clicked the phishing lure.
  - name: remediation_actions
    type: array
    description: Mail purge, proxy block, and password reset recommendations.
---

# Phishing Email Incident Response Playbook

This playbook provides automated triage, indicator extraction, and recipient scope determination for suspected phishing campaigns using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
Phishing remains a primary initial compromise vector. This playbook coordinates:
1. Analysis of message indicators (sender IP, sender domain, embedded URLs, attachments).
2. Threat reputation lookup and credential harvesting classification.
3. Determination of campaign exposure across the organization.
4. Rapid mail server purge and user credential containment proposals.

## 2. Remote MCP Tool Scope
- `summarize_entity`: Looks up reputation, categorization, and threat tags for suspect URLs, domains, and attachment hashes.
- `search_entity`: Searches the entity graph for related recipient systems and sender nodes.
- `get_ioc_matches`: Evaluates whether the phishing domain or URL matches active threat intelligence feeds.
- `list_security_alerts`: Checks for alerts related to email security or credential theft.
- `get_security_alert`: Retrieves contextual metadata from existing email gateway alerts.
- `list_cases`: Retrieves open phishing triage cases.
- `get_case`: Reads case details and assignee notes.
- `add_case_comment`: Documents triage findings and campaign exposure metrics into Chronicle SOAR.

## 3. Step-by-Step Reasoning Protocol

### Phase 1: Lure Deconstruction & Indicator Extraction
- Parse the reported message context:
  - **Sender Infrastructure**: Sender address, sending MTA IP address, return-path.
  - **Embedded Links**: Extract all hyperlinked URLs, redirect hops, and anchor tags. Defang during reporting.
  - **Attachments**: Extract filenames, file types, and SHA256 hashes.

### Phase 2: Threat Intelligence & Entity Validation
- Call `summarize_entity` on:
  - Embedded URLs/domains: Look for credential harvest signatures, login clone kits, brand impersonation.
  - Attachment hashes: Check detection ratios and sandbox analysis results.
- Call `get_ioc_matches` to see if sender infrastructure has matched global threat campaigns.

### Phase 3: Internal Scope & Recipient Exposure
- Determine organizational exposure:
  - Identify whether multiple employees received the same email subject or sender domain.
  - Check whether any internal users clicked the link or authenticated on the external domain.
  - Cross-reference proxy and DNS logs to verify if outbound traffic succeeded.

### Phase 4: Remediation & Containment
- Formulate containment steps:
  1. **Mailbox Purge**: Propose removal of the phishing message across all recipient mailboxes.
  2. **URL / Domain Block**: Propose proxy and firewall blocklist additions for the malicious domain.
  3. **Credential Invalidation**: If a user submitted credentials, initiate immediate password reset and session revocation.
  4. **User Notification**: Draft clear notification to affected employees with advice on monitoring.

### Phase 5: Case Documentation
- Call `add_case_comment` to record:
  - Phishing verdict and threat category.
  - Number of exposed recipients.
  - Recommended mail purge criteria.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous**: Indicator analysis, entity lookups, threat feed correlation, and case note documentation.
- **Approval Required**: Mass mailbox deletion/purging, domain-wide email transport rule creation, or forced user password resets require human confirmation.

## 5. Example Prompts
- *"Execute phishing response playbook on reported email with sender invoices@billing-portal-update[.]com."*
- *"Analyze attachment hash 7d9a8f... reported by HR and check if other employees received it."*

## 6. Output Schema
Deliver a structured Phishing Triage Report:
- **Playbook**: `playbook-phishing-response`
- **Verdict**: `[Malicious Phish | Credential Harvester | Benign Spam | Legitimate Comms]`
- **Sender Analysis**: Sending IP, domain age, authentication (SPF, DKIM, DMARC).
- **Lure Content**: Malicious URLs or attachment hashes identified.
- **Campaign Blast Radius**: List of affected recipients and confirmed click events.
- **Remediation Plan**: Actionable mail purge and blocklist proposals.
