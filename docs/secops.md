# Google SecOps Agent Guide - Chronicle Remote MCP Bridge

## Overview

The Google Cloud SecOps integration bridges the **Chronicle Remote Model Context Protocol (MCP)** server (`https://chronicle.googleapis.com/mcp`) with the **Google Agent Development Kit (ADK)** and **Vertex AI Agent Runtime**.

Chronicle Remote MCP exposes over 70 fine-grained SIEM and SOAR tools. Rather than exposing all 70+ tools to the model simultaneously, `google-cloud-mcp-bridge` organizes domain intelligence into **13 specialized skills, atomic runbooks, and incident playbooks**, dynamically scoping required tools to maintain optimal latency, token economy, and reasoning fidelity.

---

## SecOps Skill Catalog

The SecOps skill catalog is organized under `skills/secops/` following the standardized schema defined in `skills/secops/TEMPLATE.md`:

```text
skills/secops/
├── SKILL.md                          # Root SOC Lead Analyst & Triage Orchestrator
├── TEMPLATE.md                       # Canonical skill specification & schema contract
├── chatops/
│   └── SKILL.md                      # Incident communication, SOAR case updates, HITL
├── ioc-enrichment/
│   └── SKILL.md                      # Multi-entity IOC lookup & threat intelligence
├── malware-triage/
│   └── SKILL.md                      # File payload analysis, YARA rules, detection triage
├── runbooks/                         # Atomic entity investigation runbooks
│   ├── domain/SKILL.md               # Domain reputation, DNS resolution, WHOIS age
│   ├── hash/SKILL.md                 # Hash verification, malware family matching
│   ├── ip-address/SKILL.md           # Routing, ASN correlation, threat feeds
│   ├── url/SKILL.md                  # URL structure decomposition, phishing heuristics
│   └── user/SKILL.md                 # Identity compromise, impossible travel, audit logs
└── playbooks/                        # End-to-end incident response playbooks
    ├── compromised-account/SKILL.md  # Identity containment, session revocation
    ├── investigation-report/SKILL.md # Executive briefs, technical incident timelines
    ├── phishing-response/SKILL.md    # Phishing lure triage, mailbox purge proposals
    └── ransomware-response/SKILL.md  # Containment protocols, shadow copy checks, C2 blocks
```

---

## Tool Mapping Matrix

Each skill defines an explicit `tool_filter` in its YAML frontmatter, restricting tool access strictly to its operational domain:

| Skill / Runbook | Path | Primary Role | Allowed Chronicle MCP Tools |
| :--- | :--- | :--- | :--- |
| **Root Analyst** | `skills/secops/SKILL.md` | Lead SOC Analyst & Orchestrator | `list_rules`, `get_rule`, `get_rule_detections`, `list_security_alerts`, `get_security_alert`, `summarize_entity`, `search_entity`, `get_ioc_matches`, `list_cases`, `get_case`, `add_case_comment`, `list_reference_lists` |
| **IOC Enrichment** | `skills/secops/ioc-enrichment/SKILL.md` | Threat Intelligence Analyst | `summarize_entity`, `search_entity`, `get_ioc_matches`, `list_reference_lists` |
| **Malware Triage** | `skills/secops/malware-triage/SKILL.md` | Tier 2 Malware Responder | `summarize_entity`, `search_entity`, `list_rules`, `get_rule_detections`, `list_security_alerts`, `get_security_alert` |
| **ChatOps & HITL** | `skills/secops/chatops/SKILL.md` | Incident Commander / Collaboration Agent | `list_cases`, `get_case`, `update_case`, `close_case`, `add_case_comment` |
| **Domain Runbook** | `skills/secops/runbooks/domain/SKILL.md` | SOC Analyst (Domain Specialist) | `summarize_entity`, `search_entity`, `get_ioc_matches` |
| **IP Runbook** | `skills/secops/runbooks/ip-address/SKILL.md` | SOC Analyst (Network Specialist) | `summarize_entity`, `search_entity`, `get_ioc_matches` |
| **Hash Runbook** | `skills/secops/runbooks/hash/SKILL.md` | SOC Analyst (Payload Specialist) | `summarize_entity`, `search_entity`, `list_rules`, `get_rule_detections` |
| **URL Runbook** | `skills/secops/runbooks/url/SKILL.md` | SOC Analyst (Web Specialist) | `summarize_entity`, `search_entity`, `get_ioc_matches` |
| **User Runbook** | `skills/secops/runbooks/user/SKILL.md` | SOC Analyst (Identity Specialist) | `summarize_entity`, `search_entity`, `list_security_alerts`, `get_security_alert` |
| **Compromised Account** | `skills/secops/playbooks/compromised-account/SKILL.md` | Incident Responder (Identity) | `summarize_entity`, `search_entity`, `list_security_alerts`, `get_security_alert`, `list_cases`, `get_case`, `add_case_comment` |
| **Ransomware Response** | `skills/secops/playbooks/ransomware-response/SKILL.md` | Incident Commander (Forensics) | `summarize_entity`, `search_entity`, `list_rules`, `get_rule_detections`, `list_security_alerts`, `get_security_alert`, `list_cases`, `get_case`, `update_case`, `add_case_comment` |
| **Phishing Response** | `skills/secops/playbooks/phishing-response/SKILL.md` | SOC Analyst (Phishing Triage) | `summarize_entity`, `search_entity`, `get_ioc_matches`, `list_security_alerts`, `get_security_alert`, `list_cases`, `get_case`, `add_case_comment` |
| **Investigation Report** | `skills/secops/playbooks/investigation-report/SKILL.md` | Lead Analyst & Technical Writer | `list_cases`, `get_case`, `add_case_comment`, `summarize_entity`, `search_entity`, `list_security_alerts` |

---

## Human-in-the-Loop (HITL) Guardrails

To prevent unauthorized actions or accidental disruptions during active security incidents, all mutating actions require explicit human confirmation.

### Read Actions (Autonomous)
The agent may execute the following discovery and investigation tools autonomously without confirmation:
- `summarize_entity`, `search_entity`, `get_ioc_matches`
- `list_rules`, `get_rule`, `get_rule_detections`
- `list_security_alerts`, `get_security_alert`
- `list_cases`, `get_case`
- `list_reference_lists`

### Mutating Actions (Strict Confirmation Required)
The agent MUST pause, propose the action with full parameter details, and await explicit operator approval before calling:
- `update_case`: Modifying case priority, status, assignee, or tags.
- `close_case`: Closing or resolving a security case.
- `add_case_comment`: Writing formal investigation notes to SOAR records.
- Any external containment proposal (e.g., firewall perimeter blocks, user account suspension, mailbox purges).

**Standard Confirmation Protocol**:
```text
PROPOSED ACTION:
- Tool: update_case
- Case ID: 1042
- Changes: Set status="IN_PROGRESS", priority="HIGH"
- Justification: Confirmed active C2 beaconing to high-confidence malicious domain.

Confirm execution? (y/n)
```

---

## Example Prompts & Workflows

### 1. Multi-Entity Threat Intelligence & IOC Enrichment
```bash
just chat "Investigate domain malicious-update.net and IP 198.51.100.24. Check for active IOC matches, threat feed associations, and internal alert telemetry."
```

### 2. Compromised User Account Triage
```bash
just chat "Triage alert SEC-8921 involving user jdoe@example.com. Check for impossible travel logins, privilege escalation events, and summarize identity risk."
```

### 3. Phishing Lure Deconstruction
```bash
just chat "Analyze suspected phishing email with sender admin@secure-login-portal.org and link https://login-verify-account.com/auth. Extract indicators and recommend containment."
```

### 4. Incident Brief Generation
```bash
just chat "Generate an executive investigation report for case 4105 covering attack timeline, affected assets, containment actions taken, and remaining remediation items."
```
