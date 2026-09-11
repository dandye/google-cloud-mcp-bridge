---
name: runbook-hash
description: >
  Atomic investigation runbook for file hashes (MD5, SHA1, SHA256). Evaluates malware
  reputation via Google Threat Intelligence, correlates Chronicle YARA-L detection rules,
  and inspects endpoint process execution.
role: SOC Analyst & Malware Investigator
category: Investigation
tool_filter:
  - summarize_entity
  - search_entity
  - list_rules
  - get_rule_detections
inputs:
  - name: file_hash
    type: string
    description: File hash in MD5, SHA1, or SHA256 format.
    required: true
  - name: time_window
    type: string
    description: Historical analysis window (e.g., last 72 hours, 7 days).
    required: false
outputs:
  - name: verdict
    type: string
    description: Classification (Benign, Suspicious, Malicious, Inconclusive).
  - name: malware_classification
    type: string
    description: Threat family, suggested label, sandbox tags, and AV detection ratio.
  - name: internal_execution_scope
    type: string
    description: Affected hosts, executed command lines, file paths, and triggering detection rules.
  - name: recommended_actions
    type: array
    description: Ordered remediation, host isolation, and binary containment actions.
---

# Atomic Runbook: File Hash Investigation

This atomic runbook defines the standardized investigative procedure for cryptographic file hashes (MD5, SHA1, SHA256) using Google Cloud SecOps (Chronicle) Remote MCP tools.

## 1. Overview & Objective
File hashes are critical indicators for identifying known malware binaries, unauthorized tooling, and compromised system files. This atomic runbook provides procedures to:
1. Validate hash integrity and query external threat intelligence for reputation and malware family classification.
2. Determine whether Chronicle YARA-L detection rules have matched the binary across enterprise endpoints.
3. Identify process execution trees, parent processes, command lines, and impacted hostnames.
4. Establish threat verdicts and formulate containment workflows.

## 2. Remote MCP Tool Scope
This runbook utilizes the following Chronicle Remote MCP tools:
- `summarize_entity`: Retrieves GTI reputation scores, malware classification labels, sandbox behavioral tags, and meaningful file names for the hash.
- `search_entity`: Searches the Chronicle entity graph to identify endpoints, file paths, and users linked to the hash.
- `list_rules`: Lists active YARA-L detection rules in Chronicle to cross-reference detection logic.
- `get_rule_detections`: Pulls detections triggered by YARA-L rules for the hash across corporate endpoints.

## 3. Step-by-Step Reasoning Protocol

### Step 1: Input Normalization & Hash Format Validation
- Validate hash length and hexadecimal format:
  - MD5: 32 characters
  - SHA1: 40 characters
  - SHA256: 64 characters
- Normalize hash string to lowercase.

### Step 2: External Reputation & Malware Classification
- Call `summarize_entity` with the file hash.
- Extract:
  - GTI / VirusTotal malicious detection count and engine ratio.
  - Popular threat classification (e.g., "trojan", "ransomware", "infostealer", "downloader", "pup").
  - Behavioral tags (e.g., "persistence", "evasion", "creates-service", "injects-process").
  - Meaningful file names and original compilation metadata if available.

### Step 3: Detection Rule Correlation
- Call `list_rules` to identify active detection rules relevant to malware execution, file modifications, or credential dumping.
- Call `get_rule_detections` with the file hash or rule IDs to locate existing alerts and rule firings in Chronicle.
- Assess whether the hash triggered multiple layered detections across endpoint and network rules.

### Step 4: Enterprise Sighting & Process Context
- Call `search_entity` within the specified time_window (defaulting to 72 hours).
- Identify:
  - Endpoints (hostnames, IP addresses) where the hash was observed or executed.
  - Execution context: process command-line arguments, parent process name, full file path.
  - User accounts associated with the process launch.
  - First-seen and last-seen timestamps across the environment.

### Step 5: Synthesis & Verdict Formulation
- Weigh threat intelligence against internal sightings:
  - **Benign**: Known signed operating system component, certified administrative software, zero AV detections.
  - **Suspicious**: Unsigned utility, administrative scripting tool executed from unusual directory (e.g., %TEMP%), potentially unwanted program (PUP).
  - **Malicious**: Confirmed malware family (ransomware, backdoor, stealer), high GTI engine count, or verified unauthorized tool execution.
- Detail prioritized containment and remediation steps.

## 4. Human-in-the-Loop (HITL) Safeguards
- **Autonomous Actions**: Read-only queries for threat reputation (`summarize_entity`), entity graph sightings (`search_entity`), and rule checks (`list_rules`, `get_rule_detections`).
- **Actions Requiring Human Authorization**:
  - Isolating or quarantining endpoints where the binary executed.
  - Terminating running process trees or deleting binary files on endpoints.
  - Adding the hash to enterprise-wide EDR blocklists or AV restriction policies.
  - Revoking credentials for user accounts that executed malicious binaries.

## 5. Example Prompts
- "Perform an atomic investigation on SHA256 hash e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 to check GTI reputation and internal sightings."
- "Investigate file hash 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 to determine if it triggered any Chronicle YARA-L rules."

## 6. Output Schema & Reporting Structure
Deliver a structured investigation report:
- **Executive Summary**: 2-3 sentence overview of file classification, malware family, and internal sightings.
- **File Reputation & Threat Intelligence**:
  - File Hash: `<hash>` (`<type>`)
  - Malicious Detection Ratio: `<malicious> / <total>`
  - Suggested Threat Label: `<label>`
  - Behavioral Tags: `<tags>`
  - Common File Names: `<names>`
- **Chronicle Rule Detections & Sightings**:
  - Triggered Detection Rules: `<list_of_rules>`
  - Impacted Endpoints: `<list_of_hosts>`
  - Associated File Paths: `<paths>`
  - Process Command Lines: `<command_lines>`
  - Execution User Accounts: `<users>`
  - Timeline (UTC): `<first_seen>` to `<last_seen>`
- **Verdict**: `[Benign | Suspicious | Malicious | Inconclusive]`
- **Recommended Next Steps**: Prioritized containment, host isolation, and eradication steps with HITL authorization tags.
