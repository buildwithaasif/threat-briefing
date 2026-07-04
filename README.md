markdown
# Threat Briefing

AI-powered threat intelligence briefing for security professionals. Fetches security news, summarizes it for pentesters, maps to MITRE ATT&CK techniques, and generates actionable CLI commands - all filtered against your tech stack.

## What It Does

- Fetches security news from multiple RSS feeds
- Filters out non-security articles automatically
- Summarizes articles with LLM focused on pentester impact
- Explains threats in plain language (what's happening + why it matters)
- Maps threats to MITRE ATT&CK techniques
- Generates practical CLI commands you can run immediately
- Checks threats against your infrastructure profile (🔴 high priority, 🟡 low priority)
- Saves everything to searchable history

## Sample Output
$ python3 run.py quick


THREAT INTELLIGENCE BRIEFING


🔴 New AWS S3 Bucket Policy Exploit Allows Data Theft
📌 MATCHES YOUR STACK: AWS
📖 Attackers exploit misconfigured S3 bucket policies
to gain unauthorized access to sensitive data.
💥 Check your bucket policies immediately.
🔖 MITRE: T1190, T1530
🎯 aws s3api get-bucket-acl --bucket your-bucket-name

🟡 Critical RCE Found in Apache Struts
📖 Remote code execution in Apache Struts allows
attackers to run arbitrary code on affected servers.
💥 Test Struts endpoints for OGNL injection.
🔖 MITRE: T1190
🎯 nuclei -t cves/2026/CVE-2026-XXXXX.yaml -l targets.txt


Saved: 2 new | Total in DB: 2


text

## Quick Start

```bash
git clone https://github.com/buildwithaasif/threat-briefing.git
cd threat-briefing
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py quick
Commands
bash
python3 run.py quick          # Today's briefing
python3 run.py full           # Deeper scan (more articles)
python3 run.py history        # Past briefings
python3 run.py search <term>  # Search history
python3 run.py stats          # Database stats
Profile
Edit app/core/profiles/default.yaml with your tech stack to get prioritized alerts.

Example:

yaml
infrastructure:
  cloud:
    - AWS
  containers:
    - Docker
  os:
    - Linux
    - macOS
  tools:
    - Burp Suite
    - Metasploit
    - nuclei

ignore:
  - Windows Server
  - Azure
  - SAP
Requirements
Python 3.10+

Ollama running locally

Models: qwen3.6:latest and llama3.2:3b

bash
ollama pull qwen3.6:latest
ollama pull llama3.2:3b