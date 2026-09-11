---
name: playbook-ransomware-response
description: >
  Critical incident response playbook for ransomware outbreaks, mass encryption events,
  volume shadow copy deletions, and rapid containment orchestration.
role: Incident Commander & Forensic Specialist
category: IncidentResponse
tool_filter:
  - summarize_entity
  - search_entity
  - list_rules
  - get_rule_detections
  - list_security_alerts
  - get_security_alert
  - list_cases
  - get_case
  - update_case
  - add_case_comment
inputs:
  - name: primary_indicator
    type: string
    description: Hostname, IP address, ransomware note hash, or triggering alert ID.
    required: true
  - name: case_id
    type: string
    description: Active Chronicle SOAR incident case ID.
    required: false
outputs:
  - name: outbreak_severity
    type: string
    description: Severity rating (Catastrophic Outbreak, Contained Infection, Isolated Event).
  - name: affected_perimeter
    type: array
    description: Confirmed infected hostnames, file shares, and hypervisors.
  - name: containment_instructions
    type: array
    description: Ordered network segregation, host isolation, and C2 blocking steps.
---

# Ransomware Outbreak Incident Response Playbook

This playbook provides high-priority containment, telemetry correlation, and remediation workflows for ransomware attacks within Google Cloud SecOps.

## 1. Overview & Objective
Ransomware attacks demand rapid, decisive response. This playbook coordinates:
1. Immediate identification of the patient-zero host and active encryption vectors.
2. Rapid host-level and network-level isolation to prevent lateral propagation.
3. Preservation of forensic artifacts (memory, encrypted sample, ransom notes).
4. Continuous synchronization with Chronicle SOAR incident tracking.

## 2. Remote MCP Tool Scope
- `summarize_entity`: Evaluates ransomware binary hashes, suspect C2 domains, and infected host behavioral telemetry.
- `search_entity`: Searches the entity graph for related hostnames, shares, and lateral movement artifacts.
- `list_rules`: Identifies active Chronicle YARA-L detection rules (e.g., shadow copy deletion, mass file renaming).
- `get_rule_detections`: Pulls detections across all enterprise systems to identify the full outbreak scope.
- `list_security_alerts`: Lists critical and high severity alerts fired during the infection window.
- `get_security_alert`: Fetches execution telemetry, parent-child process chains, and command arguments.
- `list_cases`: Retrieves active incident response cases.
- `get_case`: Reads case history, severity levels, and stakeholder assignees.
- `update_case`: Escalates case severity (e.g., to CRITICAL / P0) and assigns response teams.
- `add_case_comment`: Records containment timestamps and audit logs.

## 3. Step-by-Step Reasoning Protocol

### Phase 1: Rapid Triangulation & Patient Zero
- Call `get_security_alert` or `summarize_entity` on the primary indicator.
- Identify the initial execution mechanism:
  - Malicious macro or email attachment download.
  - Vulnerable public-facing service exploitation.
  - Compromised VPN / RDP credential session.
- Extract the ransomware binary hash and known C2 contact points.

### Phase 2: Blast Radius Determination
- Call `get_rule_detections` across detection rules for:
  - Volume Shadow Copy deletion (`vssadmin delete shadows`, `wmic shadowcopy delete`).
  - BitLocker / file encryption utilities and ransom extension modifications.
  - Active directory domain controller enumeration.
- Enumerate all affected hosts, IP subnets, and compromised storage shares.

### Phase 3: Emergency Containment Protocol
- Immediately propose containment priorities:
  1. **Host Isolation**: Sever network connections on all confirmed infected endpoints.
  2. **Network Segregation**: Disconnect compromised subnets from corporate backbone and cloud environments.
  3. **Domain Account Lockouts**: Lock accounts observed executing administrative commands from patient zero.
  4. **Perimeter C2 Blocking**: Push identified C2 IP addresses and DNS domains to perimeter blocklists.

### Phase 4: Eradication & Forensic Preservation
- Preserve forensic evidence prior to host reimaging:
  - Isolate volatile memory and forensic copies of the ransomware executable.
  - Collect sample ransom notes and representative encrypted files for decryptor verification.
- Verify backup integrity: Confirm offline backups or immutable snapshots are intact and uninfected.

### Phase 5: Case Synchronization & Escalation
- Call `update_case` to set priority to `CRITICAL`.
- Call `add_case_comment` to document:
  - Confirmed patient zero hostname and IP.
  - Complete list of quarantined systems.
  - Malware family attribution.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous**: Read-only telemetry gathering, detection correlation, and case note documentation.
- **Approval Required**: Triggering host network isolation, terminating domain-wide services, or shutting down hypervisors requires explicit Incident Commander approval.

## 5. Example Prompts
- *"Execute ransomware response playbook for alert 20260911_vssadmin_delete on host win-app-srv-01."*
- *"Determine the blast radius of ransomware sample hash 8f4e91... across our Chronicle customer tenant."*

## 6. Output Schema
Deliver a structured Ransomware Incident Brief:
- **Playbook**: `playbook-ransomware-response`
- **Outbreak Severity**: `[CRITICAL - Active Outbreak | HIGH - Contained Incident | Inconclusive]`
- **Patient Zero**: Target hostname, IP, and initial execution timestamp.
- **Affected Systems**: List of quarantined hosts and exposed network segments.
- **Containment Action Plan**: Prioritized checklist of isolation and blocking actions.
- **Forensic Artifacts**: Hashes, ransom note filenames, and C2 endpoints.
