---
name: playbook-compromised-account
description: >
  End-to-end incident response playbook for investigating and containing compromised user accounts,
  anomalous authentication, impossible travel, and privilege abuse using the PICERL model.
role: Incident Responder & Identity Specialist
category: IncidentResponse
tool_filter:
  - summarize_entity
  - search_entity
  - list_security_alerts
  - get_security_alert
  - list_cases
  - get_case
  - add_case_comment
inputs:
  - name: user_identifier
    type: string
    description: Compromised username, email address, or principal ID.
    required: true
  - name: case_id
    type: string
    description: Relevant Chronicle SOAR case ID for tracking and documentation.
    required: false
  - name: time_window
    type: string
    description: Scope window for authentication and telemetry logs (default last 24 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Assessment verdict (Confirmed Compromise, Suspicious Activity, False Positive).
  - name: attack_vector
    type: string
    description: Primary intrusion mechanism (e.g., Credential Stuffing, Phishing, Session Hijacking).
  - name: blast_radius
    type: array
    description: Accessed resources, modified permissions, and anomalous sessions.
  - name: containment_status
    type: string
    description: Status of account revocation, session invalidation, and password reset recommendations.
---

# Compromised User Account Incident Response Playbook

This playbook provides a structured workflow for responding to incidents involving potentially compromised user identities using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
When impossible travel alerts fire, high-risk credentials are leaked, or abnormal administrative activity is observed, this playbook guides the agent through:
1. Verification of identity compromise likelihood.
2. Reconstruction of attacker actions under the compromised identity.
3. Rapid containment and eradication to prevent lateral movement.
4. Comprehensive documentation in Chronicle SOAR cases.

## 2. Remote MCP Tool Scope
- `summarize_entity`: Pulls the behavioral timeline, risk score, and anomaly telemetry for the user identity.
- `search_entity`: Looks up linked endpoints, IP addresses, and session contexts.
- `list_security_alerts`: Lists identity-related alerts (e.g., impossible travel, MFA fatigue, brute force).
- `get_security_alert`: Retrieves granular telemetry for specific alert triggers.
- `list_cases`: Locates open security incident cases for the user.
- `get_case`: Fetches case history, existing notes, and assigned analysts.
- `add_case_comment`: Posts investigation updates and containment status directly into the case audit log.

## 3. Step-by-Step Reasoning Protocol (PICERL Model)

### Phase 1: Preparation & Input Parsing
- Normalize the `user_identifier` (strip domain suffix or downcase as needed).
- Retrieve existing case context using `get_case` if `case_id` is provided.

### Phase 2: Identification & Activity Triangulation
- Call `summarize_entity` on the user to review:
  - Geographic login distribution over the last 24-48 hours.
  - Anomalous User-Agent strings or browser profiles.
  - Impossible travel indicators (e.g., London login followed by Tokyo login within 20 minutes).
- Call `list_security_alerts` filtered by the user entity to correlate concurrent alerts.

### Phase 3: Blast Radius & Impact Assessment
- Correlate resources accessed by the identity:
  - Privilege escalation attempts (IAM role assignments, service account impersonation).
  - Cloud storage bucket reads or large egress volumes.
  - Mail forwarding rules, OAuth application consents, or API key generations.

### Phase 4: Containment Actions
- Formulate immediate containment steps:
  1. Revoke all active OAuth tokens and web sessions.
  2. Initiate forced credential rotation / password reset.
  3. Require MFA re-registration if token compromise is suspected.
  4. Temporarily restrict sensitive group memberships.

### Phase 5: Eradication & Recovery
- Audit and remove any persistent mechanisms created during the compromise window:
  - Revoke newly granted IAM roles or API keys.
  - Delete unauthorized email forwarding or inbox rules.
  - Verify endpoints used during the session for malware presence using `summarize_entity`.

### Phase 6: Case Documentation & Lessons Learned
- Summarize findings and call `add_case_comment` to record the incident timeline in Chronicle SOAR.
- Propose identity policy hardening (e.g., conditional access, FIDO2 enforcement).

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous**: Read-only queries of user entity summaries, alert histories, and case notes.
- **Approval Required**: Disabling user accounts, revoking active sessions in production Identity Providers, or applying policy restrictions must be submitted to a human analyst for confirmation.

## 5. Example Prompts
- *"Execute the compromised account playbook for user alice@corp.example.com following an impossible travel alert."*
- *"Investigate potential credential stuffing on account admin-svc-01 and log findings to Chronicle case CASE-7701."*

## 6. Output Schema
Deliver a structured Incident Response Briefing:
- **Playbook**: `playbook-compromised-account`
- **User Identifier**: `<user_id>`
- **Verdict**: `[Confirmed Compromise | Suspicious Activity | False Positive]`
- **Compromise Timeline**: Table of timestamps, source IPs, locations, and actions.
- **Identified Threat Vector**: Suspected initial access method.
- **Recommended Containment Protocol**: Ordered containment steps with HITL authorization flags.
- **SOAR Audit Log**: Confirmation of case comments posted.
