---
name: runbook-user
description: >
  Atomic investigation runbook for user identities and accounts. Evaluates user risk profiles,
  reviews security alerts in Chronicle SIEM, inspects authentication patterns, and assesses compromise.
role: SOC Analyst & Identity Investigator
category: Investigation
tool_filter:
  - summarize_entity
  - search_entity
  - list_security_alerts
  - get_security_alert
inputs:
  - name: username
    type: string
    description: Username, User Principal Name (UPN), or user ID under investigation.
    required: true
  - name: time_window
    type: string
    description: Historical analysis window (e.g., last 24 hours, 72 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Compromised, Inconclusive).
  - name: risk_profile
    type: string
    description: Baseline behavior, account type, accessed assets, and risk rating.
  - name: security_alerts_summary
    type: string
    description: Active alerts, triggered detection rules, and anomalous activity details.
  - name: recommended_actions
    type: array
    description: Ordered remediation, session revocation, or credential reset actions.
---

# Atomic Runbook: User Identity Investigation

This atomic runbook defines the standardized investigative procedure for user identities and accounts using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
User accounts are high-value targets for credential stuffing, phishing, privilege escalation, and insider threats. This atomic runbook provides procedures to:
1. Establish identity context, account role, and baseline behavior.
2. Enumerate security alerts and detections associated with the user in Chronicle SIEM.
3. Analyze authentication events, anomalous logons, accessed hosts, and process executions.
4. Establish risk verdicts and formulate identity containment workflows.

## 2. Remote MCP Tool Scope
This runbook utilizes the following Chronicle Remote MCP tools:
- `summarize_entity`: Obtains user risk scores, baseline activity profiles, linked assets, and entity summaries.
- `search_entity`: Searches the Chronicle entity graph to identify logon events, host sessions, and resource access for the user.
- `list_security_alerts`: Lists active and historical security alerts involving the user account within the investigation window.
- `get_security_alert`: Fetches complete context, triggering rules, and event payloads for specific user-related alerts.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Input Normalization & Identity Resolution
- Normalize username format (e.g., sAMAccountName, user@domain.com, userPrincipalName, or UDM principal.user.userid).
- Determine account classification:
  - Corporate employee / human user
  - Privileged administrator account
  - Service account / API identity / machine credential
- Note elevated privileges or sensitive access rights associated with the identity.

### Step 2: Entity Profiling & Activity Baseline
- Call `summarize_entity` with the username.
- Extract:
  - Chronicle entity risk score and anomaly indicators.
  - Typical working hours, primary devices/workstations, and routinely accessed systems.
  - First-seen and last-seen activity timestamps.

### Step 3: Security Alert Triaging
- Call `list_security_alerts` for the user within the time_window (defaulting to 72 hours).
- Review all triggered alerts (e.g., impossible travel, brute-force attempts, anomalous resource access).
- For high-priority alerts, call `get_security_alert` to inspect:
  - Detection rule name and description.
  - Associated network indicators, source IP addresses, and user agents.
  - Security result action (e.g., ALLOW, BLOCK).

### Step 4: Enterprise Sighting & Behavioral Correlation
- Call `search_entity` to review recent user actions in Chronicle:
  - Authentication patterns: successful logins, repeated failed attempts, logins from unusual source IPs or geolocations.
  - Systems accessed: lateral movement between distinct hosts, unusual administrative tool execution.
  - Process launch activity initiated by the user account on target endpoints.

### Step 5: Synthesis & Verdict Formulation
- Weigh baseline normality against observed anomalies:
  - **Benign**: Expected administrator maintenance, standard user activity during normal business hours, authorized access.
  - **Suspicious**: Unexplained failed logons from foreign IP, login from anomalous VPN endpoint, or access to non-standard systems without confirmed malicious activity.
  - **Compromised**: Confirmed account takeover (ATO), impossible travel with successful authentication, unauthorized credential dumping or lateral movement under user context.
- Formulate prioritized identity containment recommendations.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only queries for user profile (`summarize_entity`), entity graph searches (`search_entity`), alert listing (`list_security_alerts`), and alert inspection (`get_security_alert`).
- **Actions Requiring Human Authorization**:
  - Terminating active user sessions or revoking OAuth / refresh tokens.
  - Disabling or locking user accounts in Identity Providers (Google Workspace, Active Directory, Okta).
  - Resetting passwords or enforcing immediate MFA re-enrollment.
  - Restricting user access to production infrastructure or sensitive data repositories.

## 5. Example Prompts
- "Perform an atomic user investigation on jdoe@example.com following an impossible travel security alert."
- "Investigate user account svc-deployer to review recent Chronicle alerts, accessed systems, and authentication patterns."

## 6. Output Schema & Reporting Structure
Deliver a structured investigation report:
- **Executive Summary**: 2-3 sentence synthesis of user risk, account type, and findings.
- **User Identity Profile**:
  - Account: `<username>`
  - Classification: `[Employee | Privileged Admin | Service Account]`
  - Risk Score / State: `<risk_score>`
  - Primary Devices: `<list_of_devices>`
- **Security Alerts & Detections**:
  - Total Alerts: `<alert_count>`
  - Triggered Rules: `<list_of_rules>`
  - Key Alert IDs: `<list_of_alert_ids>`
- **Authentication & Behavioral Telemetry**:
  - Logon Activity: `<successful_count> successful, <failed_count> failed`
  - Source IPs / Geolocations: `<source_ips>`
  - Accessed Target Systems: `<list_of_targets>`
  - Timeline (UTC): `<first_seen>` to `<last_seen>`
- **Verdict**: `[Benign | Suspicious | Compromised | Inconclusive]`
- **Recommended Next Steps**: Prioritized identity containment, session termination, and credential remediation steps with HITL authorization requirements.
