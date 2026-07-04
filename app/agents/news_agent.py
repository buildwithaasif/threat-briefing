import feedparser
from datetime import datetime
from ollama import chat
import json
from pathlib import Path
import sys

# Add parent to path so we can import config
sys.path.append(str(Path(__file__).parent.parent))
from core.config import NEWS_FEEDS, CACHE_DIR, MODEL_HEAVY  # MODEL_HEAVY for summaries


class NewsAgent:
    """Fetches security news and summarizes with LLM"""
    
    def __init__(self):
        self.feeds = NEWS_FEEDS
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def fetch_feed(self, feed_url: str, limit: int = 3):
        """Grab latest articles from a feed"""
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": feed_url
            })
        
        return articles
    
    def summarize_article(self, article: dict) -> dict:
        """Use Qwen to extract what matters for pentesters"""
        
        prompt = f"""You are a threat intelligence analyst. Read this security article and extract:
1. One-line summary (max 20 words)
2. What was exploited/vulnerable? (technique, CVE, tool)
3. Who is affected? (tech stack, vendor, user type)
4. Practical impact for a penetration tester (one sentence)

Article Title: {article['title']}
Article Summary: {article['summary']}

Respond ONLY with JSON format:
{{"summary": "...", "vulnerability": "...", "affected": "...", "pentester_impact": "..."}}
"""
        
        response = chat(
            model=MODEL_HEAVY,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            analysis = json.loads(response['message']['content'])
        except json.JSONDecodeError:
            analysis = {
                "summary": article['title'],
                "vulnerability": "Parse failed",
                "affected": "Unknown",
                "pentester_impact": "Check article directly"
            }
        
        return {**article, **analysis}
    
    def get_latest_briefs(self, articles_per_feed: int = 2):
        """Main method: fetch all feeds, skip non-security, then summarize"""
        all_articles = []
        raw_articles = []
        
        # Phase 1: Just fetch, no LLM yet
        for feed_url in self.feeds:
            try:
                articles = self.fetch_feed(feed_url, limit=articles_per_feed)
                raw_articles.extend(articles)
            except Exception as e:
                print(f"  ✗ Failed {feed_url}: {e}")
        
        # Phase 2: Quick keyword filter - skip obvious non-security articles
        security_keywords = [
            'exploit', 'vulnerability', 'cve-', 'attack', 'malware',
            'ransomware', 'phishing', 'breach', 'zero-day', 'bug',
            'patch ', 'bypass', 'hack', 'seize', 'takedown', 'backdoor',
            'advisory', 'flaw', 'injection', 'overflow', 'leak',
            'stealer', 'trojan', 'rootkit', 'spyware', 'botnet',
            'credential', 'dump', 'escalation', 'payload', 'shell'
        ]

        for article in raw_articles:
            text = f"{article['title']} {article['summary']}".lower()
            if any(kw in text for kw in security_keywords):
                analyzed = self.summarize_article(article)
                all_articles.append(analyzed)
                print(f"  ✓ {analyzed['title'][:80]}...")
            else:
                print(f"  ⊘ Skipped (non-security): {article['title'][:60]}...")
        
        return all_articles


if __name__ == "__main__":
    # Test the agent standalone
    agent = NewsAgent()
    print("[*] Fetching latest security news...\n")
    briefs = agent.get_latest_briefs(articles_per_feed=1)
    
    print(f"\n[+] Got {len(briefs)} articles\n")
    for brief in briefs:
        print(f"📰 {brief['title']}")
        print(f"   Summary: {brief['summary']}")
        print(f"   Pentester Impact: {brief['pentester_impact']}")
        print(f"   Link: {brief['link']}\n")
