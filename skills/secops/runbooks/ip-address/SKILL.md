---
name: runbook-ip-address
description: >
  Atomic investigation runbook for IPv4 and IPv6 addresses. Assesses external reputation,
  identifies internal sightings, and inspects network communication in Chronicle SIEM.
role: SOC Analyst & Network Investigator
category: Investigation
tool_filter:
  - summarize_entity
  - search_entity
  - get_ioc_matches
inputs:
  - name: ip_address
    type: string
    description: IPv4 or IPv6 address under investigation.
    required: true
  - name: time_window
    type: string
    description: Historical time window for log and entity lookups (e.g., last 24 hours, 72 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious, Inconclusive).
  - name: reputation_summary
    type: string
    description: GTI reputation score, ASN owner, geolocation, and threat categorization.
  - name: enterprise_activity
    type: string
    description: Internal communication details, contacted ports, protocols, and host sightings.
  - name: recommended_actions
    type: array
    description: Ordered remediation, network blocking, or host isolation actions.
---

# Atomic Runbook: IP Address Investigation

This atomic runbook defines the standardized investigative procedure for IP addresses (IPv4 and IPv6) using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
IP addresses are fundamental indicators in network security alerts, perimeter logging, and endpoint telemetry. This atomic runbook provides focused procedures to:
1. Enrich external IP addresses with threat intelligence, ASN ownership, and geolocation.
2. Differentiate between internal enterprise addresses (RFC 1918 / RFC 4193) and routable external indicators.
3. Detect internal enterprise interactions, including communicating hosts, ports, protocols, and data directions.
4. Establish risk verdicts and formulate containment workflows.

## 2. Remote MCP Tool Scope
This runbook utilizes the following Chronicle Remote MCP tools:
- `summarize_entity`: Obtains GTI threat reputation scores, ASN ownership, geolocation, and behavioral timeline for the IP address.
- `search_entity`: Searches the Chronicle entity graph to identify internal assets, network connections, and activity linked to the IP.
- `get_ioc_matches`: Checks historical telemetry for matches against threat intelligence indicator feeds.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Input Normalization & Address Classification
- Validate IP format (IPv4 or IPv6).
- Check against non-routable and private address spaces:
  - RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Loopback (`127.0.0.0/8`) and Link-Local (`169.254.0.0/16`)
  - RFC 4193 IPv6 Unique Local (`fc00::/7`) and Link-Local (`fe80::/10`)
- If the target is an internal private IP, pivot analysis toward internal asset triage rather than external GTI reputation lookups.

### Step 2: External Reputation & Threat Intelligence
- For external routable IPs, call `summarize_entity`.
- Extract:
  - GTI / VirusTotal malicious, suspicious, and harmless scores.
  - Autonomous System Number (ASN) and AS owner.
  - Geolocation (country, region).
  - Threat categories (e.g., "scanner", "botnet", "tor-exit-node", "c2", "bulletproof-hosting").
  - Identify whether the IP belongs to a reputable cloud provider (GCP, AWS, Azure) or CDN, which may indicate shared or hijacked infrastructure.

### Step 3: Threat Intelligence Feed Correlation
- Call `get_ioc_matches` for the IP address.
- Review feed match metadata: provider attribution, confidence level, and first/last match dates.
- Check whether the IP is recognized on active commercial or open-source threat feeds.

### Step 4: Enterprise Sightings & Network Correlation
- Call `search_entity` to evaluate internal telemetry within the specified time_window (defaulting to 24-72 hours).
- Identify:
  - Internal hosts and client IPs communicating with the address.
  - Directionality: Inbound connections (scanning, exploitation attempts) vs. outbound connections (beaconing, exfiltration).
  - Contacted destination ports and application protocols (e.g., port 443 HTTPS, port 80 HTTP, port 22 SSH, non-standard high ports).
  - First-seen and last-seen timestamps.

### Step 5: Synthesis & Verdict Formulation
- Correlate external intelligence with internal communication patterns:
  - **Benign**: Known enterprise SaaS provider, verified CDN, or sanctioned external service with zero threat detections.
  - **Suspicious**: Low-reputation VPS provider, anonymizing proxy / Tor exit node with limited internal connections, or opportunistic external scanner.
  - **Malicious**: Active C2 node, confirmed botnet infrastructure, high GTI detection score, or outbound data transfer to an untrusted endpoint.
- Define prioritized containment actions.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only queries for threat intelligence (`summarize_entity`), entity graph correlation (`search_entity`), and IOC match lookups (`get_ioc_matches`).
- **Actions Requiring Human Authorization**:
  - Initiating edge firewall blocks, ACL updates, or routing null-routes.
  - Quarantining or isolating internal communicating endpoints.
  - Modifying perimeter intrusion prevention system (IPS) rules.

## 5. Example Prompts
- "Perform an atomic investigation on external IP 198.51.100.45 observed in outbound firewall alerts over the last 12 hours."
- "Investigate IP address 203.0.113.88 to determine GTI reputation, ASN ownership, and internal host connections."

## 6. Output Schema & Reporting Structure
Deliver a structured investigation report:
- **Executive Summary**: 2-3 sentence overview of IP classification, reputation, and enterprise exposure.
- **Threat Intelligence & Context**:
  - IP Address: `<ip_address>`
  - Classification: `[Public Routable | Private RFC 1918 / 4193]`
  - Reputation Scores: `<malicious> / <suspicious> / <harmless>`
  - ASN & Owner: `<asn> (<as_owner>)`
  - Geolocation: `<country>`
  - Threat Categories: `<categories>`
- **Internal Enterprise Sightings**:
  - IOC Matches: `<match_count>`
  - Communicating Hosts: `<list_of_hosts>`
  - Traffic Direction & Ports: `<direction>` | `<ports>`
  - Activity Window (UTC): `<first_seen>` to `<last_seen>`
- **Verdict**: `[Benign | Suspicious | Malicious | Inconclusive]`
- **Recommended Next Steps**: Actionable firewall blocking and endpoint triage steps with HITL authorization requirements.
