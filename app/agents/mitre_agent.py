import json
import re
import sys
from pathlib import Path
from ollama import chat

sys.path.append(str(Path(__file__).parent.parent))
from core.config import KB_DIR, MODEL_LIGHT


class MITREAgent:
    """Matches news articles to MITRE ATT&CK techniques"""
    
    def __init__(self):
        self.techniques = self._load_techniques()
    
    def _load_techniques(self):
        with open(KB_DIR / 'mitre_techniques.json', 'r') as f:
            return json.load(f)
    
    def _extract_json(self, text: str) -> dict:
        """Robust JSON extraction - handles comments and truncation"""
        # Remove JavaScript-style comments
        text = re.sub(r'//.*?\n', '\n', text)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Try to find and fix truncated JSON objects
        match = re.search(r'\{.*', text, re.DOTALL)
        if match:
            json_str = match.group()
            # If truncated (missing closing brace), try to fix it
            if json_str.count('{') > json_str.count('}'):
                # Add missing closing braces
                missing = json_str.count('{') - json_str.count('}')
                json_str = json_str.rstrip() + '\n' + '}' * missing
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try adding comma before closing if needed
                json_str = re.sub(r'(\s+)$', '', json_str)  # Remove trailing whitespace
                if not json_str.endswith(','):
                    json_str += '\n}'
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        # Try JSON array
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        return None
    
    def analyze_article(self, article: dict) -> dict:
        """Analyze one article - returns technique IDs, explanation, and CLI command"""
        
        prompt = f"""You are a senior penetration tester explaining a threat to a colleague.

Article: {article['title']}
Summary: {article.get('summary', '')[:200]}
Pentester angle: {article.get('pentester_impact', '')}

Respond with JSON only:
{{
    "technique_ids": ["TXXXX"],
    "whats_happening": "Explain in 2-3 plain sentences: what the attack is, how it works technically, and why it matters to a pentester. Use simple language.",
    "command": "One practical CLI command to test for this vulnerability or detect this activity"
}}

Pick technique IDs from: T1059 (Command/scripting), T1566 (Phishing), T1203 (Exploitation), T1190 (Public-facing app), T1078 (Valid accounts), T1556 (Modify auth), T1003 (Credential dumping), T1055 (Process injection), T1583 (Infrastructure), T1040 (Sniffing), T1110 (Brute force), T1562 (Defense evasion), T1486 (Encrypt data)"""

        response = chat(
            model=MODEL_LIGHT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._extract_json(response['message']['content'])
        
        if result and isinstance(result, dict):
            return {
                "technique_ids": result.get("technique_ids", []),
                "whats_happening": result.get("whats_happening", "No explanation available."),
                "command": result.get("command", "No command generated")
            }
        
        return {
            "technique_ids": [],
            "whats_happening": "Analysis failed.",
            "command": "Check article directly"
        }


if __name__ == "__main__":
    agent = MITREAgent()
    
    sample = {
        "title": "NetNut Proxy Takedown",
        "summary": "FBI seized NetNut residential proxy network used for attacks",
        "pentester_impact": "Proxy testing infrastructure may be affected"
    }
    
    print("[*] Testing single article analysis...")
    result = agent.analyze_article(sample)
    print(json.dumps(result, indent=2))