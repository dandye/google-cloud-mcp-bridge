---
name: runbook-domain
description: >
  Atomic investigation runbook for domain names and FQDNs. Enriches domain reputation
  with Google Threat Intelligence, queries Chronicle SIEM for internal DNS resolutions
  and network connections, and assesses threat risk.
role: SOC Analyst & Domain Investigator
category: Investigation
tool_filter:
  - summarize_entity
  - search_entity
  - get_ioc_matches
inputs:
  - name: domain_name
    type: string
    description: Fully qualified domain name or hostname under investigation.
    required: true
  - name: time_window
    type: string
    description: Historical analysis window (e.g., last 24 hours, 72 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious, Inconclusive).
  - name: threat_reputation
    type: string
    description: GTI reputation score, categorization, and WHOIS registration context.
  - name: internal_prevalence
    type: string
    description: Count of internal DNS resolutions, communicating hosts, and resolved IPs.
  - name: recommended_actions
    type: array
    description: Ordered remediation, DNS sinkhole, or escalation actions.
---

# Atomic Runbook: Domain Investigation

This atomic runbook defines the standardized investigative procedure for domain names and Fully Qualified Domain Names (FQDNs) using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
Domains frequently serve as indicators in phishing campaigns, malware command-and-control (C2) communication, and data staging. This atomic runbook provides granular, single-purpose procedures to:
1. Determine external reputation, categorization, and registration history via threat intelligence.
2. Identify internal enterprise interactions, including DNS queries, resolving endpoints, and network connections.
3. Formulate risk verdicts and actionable containment workflows.

## 2. Remote MCP Tool Scope
This runbook utilizes the following Chronicle Remote MCP tools:
- `summarize_entity`: Retrieves Google Threat Intelligence (GTI) / VirusTotal reputation, risk score, threat categories, WHOIS metadata, and behavioral timeline for the domain.
- `search_entity`: Searches the Chronicle entity graph to identify internal assets querying the domain or connecting to its resolved infrastructure.
- `get_ioc_matches`: Verifies whether the domain has matched historical IOC threat feeds in the environment.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Input Normalization & Validation
- Sanitize and defang or refang the input domain (e.g., convert evil-domain[.]com to evil-domain.com).
- Strip protocol schemes (http://, https://), trailing slashes, and URL paths to isolate the root domain or FQDN.
- Validate FQDN structure. Check whether the domain is an internal enterprise zone, sanctioned partner, or known corporate asset.

### Step 2: External Reputation & Threat Intelligence
- Call `summarize_entity` with the target domain.
- Extract:
  - GTI / VirusTotal engine malicious and suspicious detection scores.
  - Threat categories (e.g., "phishing", "malware", "c2", "dynamic-dns").
  - WHOIS registration creation date and registrar. Flag domains registered within the last 30 days as newly registered domains (NRDs).
  - Historical IP resolutions associated with the domain.

### Step 3: Historical Threat Feed Correlation
- Call `get_ioc_matches` for the domain.
- Review matched threat intelligence feeds, confidence scores, and rule associations.
- Identify if the domain is tracked on active global threat feeds or enterprise watchlists.

### Step 4: Internal Enterprise Sighting & Correlation
- Call `search_entity` using the domain and its resolved IPs within the specified time_window (defaulting to 72 hours).
- Identify:
  - Internal clients and hostnames querying the domain via DNS.
  - Endpoints establishing direct network connections to resolved IPs.
  - First-seen and last-seen timestamps in enterprise telemetry.

### Step 5: Synthesis & Verdict Formulation
- Weigh collected evidence:
  - **Benign**: Legitimate enterprise domain, major CDN, established business service, zero malicious detections.
  - **Suspicious**: Newly registered domain (<30 days), dynamic DNS provider, low-confidence threat feed match, or unusual DNS query volume.
  - **Malicious**: Known C2 infrastructure, confirmed phishing landing page, multi-engine malicious rating, or active IOC feed match.
- Formulate recommended containment and remediation steps.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only threat intelligence lookups (`summarize_entity`), entity graph searches (`search_entity`), and IOC feed queries (`get_ioc_matches`).
- **Actions Requiring Human Authorization**:
  - Submitting perimeter DNS sinkhole or firewall domain block requests.
  - Isolating internal endpoints observed resolving or connecting to confirmed malicious domains.
  - Adding domains to permanent enterprise blocklists or SIEM exclusion lists.

## 5. Example Prompts
- "Perform an atomic domain investigation on login-service-verify[.]net observed in outbound DNS queries over the last 24 hours."
- "Investigate domain update-cdn-worker.xyz to check GTI reputation, WHOIS age, and internal host sightings."

## 6. Output Schema & Reporting Structure
Deliver a structured investigation report:
- **Executive Summary**: 2-3 sentence synthesis of domain risk and internal exposure.
- **Threat Intelligence & Reputation**:
  - Domain: `<domain_name>`
  - Malicious / Suspicious Score: `<score>`
  - Threat Categories: `<categories>`
  - Registrar & Creation Date: `<registrar>` | `<creation_date>`
  - Historical Resolutions: `<list_of_ips>`
- **Internal Enterprise Sightings**:
  - Detections / IOC Matches: `<match_count>`
  - Resolving Client Endpoints: `<list_of_hosts>`
  - First Seen / Last Seen (UTC): `<timestamps>`
- **Verdict**: `[Benign | Suspicious | Malicious | Inconclusive]`
- **Recommended Next Steps**: Prioritized containment, DNS sinkholing, and host isolation steps with HITL authorization flags.
