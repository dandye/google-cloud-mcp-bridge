---
name: runbook-url
description: >
  Atomic investigation runbook for URLs. Analyzes web threat reputation, evaluates
  redirection chains, checks IOC feeds, and identifies internal client access in Chronicle SIEM.
role: SOC Analyst & Web Threat Investigator
category: Investigation
tool_filter:
  - summarize_entity
  - search_entity
  - get_ioc_matches
inputs:
  - name: url
    type: string
    description: Full URL under investigation.
    required: true
  - name: time_window
    type: string
    description: Historical analysis window (e.g., last 24 hours, 72 hours).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious, Inconclusive).
  - name: url_threat_context
    type: string
    description: GTI reputation, threat categorization, final destination URL, and redirection hops.
  - name: internal_access_scope
    type: string
    description: Endpoints and user identities observed accessing the URL, HTTP response codes, and timestamps.
  - name: recommended_actions
    type: array
    description: Ordered remediation, web gateway blocking, or credential reset actions.
---

# Atomic Runbook: URL Investigation

This atomic runbook defines the standardized investigative procedure for Uniform Resource Locators (URLs) using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
URLs are primary attack vectors in phishing, credential harvesting, drive-by downloads, and web-based malware distribution. This atomic runbook provides procedures to:
1. Analyze the full URL, query strings, and destination endpoints for threat reputation.
2. Unpack redirection chains and identify final destination URLs.
3. Search Chronicle SIEM for internal endpoints accessing the URL and evaluate HTTP transaction details.
4. Establish risk verdicts and formulate containment workflows.

## 2. Remote MCP Tool Scope
This runbook utilizes the following Chronicle Remote MCP tools:
- `summarize_entity`: Obtains GTI threat reputation scores, categorization (phishing, malware), redirection hops, and final URL.
- `search_entity`: Searches the Chronicle entity graph to identify internal assets, user accounts, and proxy events linked to the URL.
- `get_ioc_matches`: Checks historical telemetry for matches against threat intelligence indicator feeds.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Input Normalization & URL Parsing
- Defang or refang the target URL (e.g., convert hxxps://bad[.]com/path to https://bad.com/path).
- Parse URL components: scheme (http, https), host/domain, port, path, and query parameters.
- Extract the root domain and FQDN for correlated domain reputation checks.
- Detect URL obfuscation, unusual encoding, or IP-based hosts (e.g., http://192.0.2.1/file).

### Step 2: External Reputation & Redirection Analysis
- Call `summarize_entity` with the full URL.
- Extract:
  - GTI / VirusTotal engine malicious, suspicious, and harmless scores.
  - Threat categories (e.g., "phishing", "malware", "exploit", "benign").
  - Final destination URL and redirection chain details. Note if the final landing page diverges from the initial indicator.
  - Threat actor attribution or campaign associations if cataloged by GTI.

### Step 3: Threat Intelligence Feed Correlation
- Call `get_ioc_matches` for the URL.
- Verify whether the exact URL or parent domain has matched active threat feeds.
- Review feed confidence and attribution.

### Step 4: Enterprise Sightings & HTTP Telemetry
- Call `search_entity` within the specified time_window (defaulting to 24-72 hours).
- Identify:
  - Internal hosts and client IPs that accessed the URL.
  - User accounts linked to the web proxy or browser events.
  - HTTP request methods (GET vs. POST). HTTP POST requests to suspicious URLs may indicate submitted credentials or form data.
  - HTTP status codes (e.g., 200 OK, 302 Found, 403 Forbidden, 404 Not Found) to determine if payload delivery succeeded.
  - First-seen and last-seen access timestamps.

### Step 5: Synthesis & Verdict Formulation
- Correlate external intelligence with internal access:
  - **Benign**: Known enterprise web application, clean content delivery network, verified partner portal with zero detections.
  - **Suspicious**: Uncategorized newly registered domain, shortened URL with multiple redirects, or low-reputation landing page.
  - **Malicious**: Confirmed credential phishing page, malware dropper URL, active C2 endpoint, or multi-engine malicious rating.
- Recommend containment actions based on exposure (e.g., whether credentials were submitted or payloads downloaded).

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only threat reputation lookups (`summarize_entity`), entity graph searches (`search_entity`), and IOC feed queries (`get_ioc_matches`).
- **Actions Requiring Human Authorization**:
  - Adding URLs or domains to secure web gateway (SWG) or proxy blocklists.
  - Purging phishing messages containing the URL from enterprise mailboxes.
  - Revoking credentials and enforcing password resets for users who submitted data to malicious URLs.
  - Quarantining endpoints that downloaded files from malicious URLs.

## 5. Example Prompts
- "Perform an atomic investigation on suspicious URL https://secure-login.account-update.net/auth/login reported from an employee phishing email."
- "Investigate URL http://198.51.100.12/update.bin accessed by workstation-04 to determine threat reputation and download status."

## 6. Output Schema & Reporting Structure
Deliver a structured investigation report:
- **Executive Summary**: 2-3 sentence overview of URL classification, threat category, and internal exposure.
- **Threat Intelligence & Redirection**:
  - Queried URL: `<url>`
  - Malicious Detection Score: `<malicious> / <total>`
  - Threat Categories: `<categories>`
  - Final Landing URL: `<final_url>`
  - Redirection Chain: `<list_of_redirects>`
- **Internal Enterprise Sightings**:
  - IOC Feed Matches: `<match_count>`
  - Accessing Endpoints: `<list_of_hosts>`
  - Impacted User Accounts: `<list_of_users>`
  - HTTP Method & Status: `<method>` | `<status_code>`
  - Access Timeline (UTC): `<first_seen>` to `<last_seen>`
- **Verdict**: `[Benign | Suspicious | Malicious | Inconclusive]`
- **Recommended Next Steps**: Prioritized gateway blocking, mailbox purging, and credential containment steps with HITL authorization requirements.
