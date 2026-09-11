---
name: ioc-enrichment
description: >
  Extracts, contextualizes, and evaluates Indicators of Compromise (IPs, domains, URLs, hashes)
  against Chronicle SIEM entity graphs, IOC matches, and threat intelligence feeds.
role: Threat Intelligence Analyst
category: Enrichment
tool_filter:
  - summarize_entity
  - search_entity
  - get_ioc_matches
  - list_reference_lists
inputs:
  - name: indicator_value
    type: string
    description: Raw IOC (IPv4, IPv6, Domain, URL, MD5, SHA1, SHA256).
    required: true
  - name: indicator_type
    type: string
    description: Explicit type (ip, domain, url, hash) if known.
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious).
  - name: reputation_summary
    type: string
    description: Summary of external GTI / VT threat signals and confidence rating.
  - name: internal_prevalence
    type: string
    description: Number of internal sightings and affected assets in Chronicle SIEM.
---

# Indicator of Compromise (IOC) Enrichment Skill

This skill provides systematic extraction, contextualization, and risk evaluation for Indicators of Compromise (IOCs) using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
Given raw indicators extracted from alerts, network logs, or analyst queries, this skill determines:
1. Whether the indicator is known malicious, suspicious, or benign.
2. How prevalent the indicator is within the internal enterprise environment.
3. What containment or blocklisting actions should be taken.

## 2. Remote MCP Tool Scope
This skill utilizes a focused subset of Chronicle MCP tools:
- `summarize_entity`: Retrieves Google Threat Intelligence (GTI) / VirusTotal reputation, risk score, and behavioral timeline for an entity.
- `search_entity`: Searches the entity graph by IP, domain, hostname, or hash.
- `get_ioc_matches`: Checks whether historical Chronicle log events have matched this indicator against threat feeds.
- `list_reference_lists`: Inspects company blocklists, allowlists, and watchlists.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Indicator Parsing & Type Validation
- Parse the input string into a standardized indicator format.
- Identify the type:
  - **IP Address**: Verify IPv4/IPv6 format. Check for private/unroutable ranges (RFC 1918 `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, Loopback `127.0.0.0/8`). Private addresses must not be flagged as external malicious indicators.
  - **Domain / URL**: Defang or refang as needed. Strip protocols and URI paths when evaluating root domain reputation.
  - **Hash**: Validate length and hex characters (MD5: 32 chars, SHA1: 40 chars, SHA256: 64 chars).

### Step 2: Internal SIEM Entity Lookup
- Execute `search_entity` or `summarize_entity` with the indicator value.
- Extract:
  - Threat score and confidence level.
  - First seen and last seen timestamps.
  - Associated threat actor groups or malware families.

### Step 3: Historical Threat Feed Correlation
- Execute `get_ioc_matches` for the indicator.
- Review matched threat intelligence feeds, feed provider attribution, and matching rule detections.
- Check `list_reference_lists` to see if the indicator is already tracked on enterprise watchlists or sanctioned allowlists.

### Step 4: Verdict Formulation & Reporting
- Assign a clear verdict:
  - **Benign**: Known clean infrastructure, major CDN, sanctioned enterprise services.
  - **Suspicious**: Low-reputation dynamic DNS, newly registered domain (<30 days), single low-confidence threat feed match.
  - **Malicious**: Confirmed C2, active malware distribution, multi-source GTI malicious verdict.
- Formulate actionable recommendations (e.g., firewall blocklist, proxy sinkhole, host isolation).

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous**: Entity lookup, IOC matching, and reference list inspection are non-destructive read operations.
- **Approval Required**: Adding indicators to production blocking reference lists or triggering perimeter firewall blocks requires human confirmation.

## 5. Example Prompts
- *"Enrich IP address 198.51.100.45 and tell me if it appears in our Chronicle IOC matches."*
- *"Check the reputation of hash 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 in our SecOps tenant."*
- *"Is the domain update-service-cdn[.]xyz classified as malicious by Chronicle threat intelligence?"*

## 6. Output Schema
Deliver a structured markdown report:
- **Indicator**: `<value>` (`<type>`)
- **Verdict**: `[Benign | Suspicious | Malicious]`
- **Threat Intelligence Context**: Reputation score, malware associations, threat actors.
- **Enterprise Sightings**: Chronicle detections, match count, affected systems.
- **Recommended Action**: Recommended containment or monitoring steps.
