markdown
# Threat Briefing

AI-powered threat intelligence briefing for security professionals. Fetches security news, summarizes it for pentesters, maps to MITRE ATT&CK techniques, and generates actionable CLI commands - all filtered against your tech stack.

## What It Does

- Fetches security news from multiple RSS feeds
- Summarizes articles with LLM (Qwen 3.6) focused on pentester impact
- Maps threats to MITRE ATT&CK techniques (Llama 3.2)
- Generates practical CLI commands you can run immediately
- Filters threats against your infrastructure profile
- Saves everything to searchable history

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
