import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.news_agent import NewsAgent
from agents.mitre_agent import MITREAgent
from core.database import BriefingDB
from core.profiler import InfrastructureProfiler


class ThreatOrchestrator:
    """Coordinates News + MITRE analysis into a complete briefing"""
    
    def __init__(self):
        self.news_agent = NewsAgent()
        self.mitre_agent = MITREAgent()
    
    def generate_briefing(self, articles_per_feed: int = 1):
        """Run full pipeline"""
        start_time = time.time()
        
        print("[*] Phase 1/3: Fetching news...")
        articles = self.news_agent.get_latest_briefs(articles_per_feed)
        
        if not articles:
            return {"error": "No articles fetched", "briefs": []}
        
        print(f"\n[*] Phase 2/3: MITRE analysis ({len(articles)} articles)...")
        briefs = []
        profiler = InfrastructureProfiler()
        
        for i, article in enumerate(articles, 1):
            print(f"  [{i}/{len(articles)}] {article['title'][:60]}...")
            analysis = self.mitre_agent.analyze_article(article)
            relevance = profiler.check_relevance(
                f"{article['title']} {article.get('summary', '')}"
            )
            
            briefs.append({
                "title": article['title'],
                "link": article['link'],
                "source": article['source'],
                "published": article.get('published', ''),
                "summary": article.get('summary', ''),
                "vulnerability": article.get('vulnerability', ''),
                "affected": article.get('affected', ''),
                "pentester_impact": article.get('pentester_impact', ''),
                "whats_happening": analysis.get('whats_happening', ''),
                "priority": relevance['priority'],
                "matched_tech": relevance['matched'],
                "mitre_techniques": analysis.get('technique_ids', []),
                "tactical_takeaway": analysis.get('command', 'No command')
            })
        
        elapsed = time.time() - start_time
        print(f"\n[*] Phase 3/3: Done in {elapsed:.1f}s")
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(briefs),
            "briefs": briefs
        }


if __name__ == "__main__":
    orchestrator = ThreatOrchestrator()
    db = BriefingDB()
    
    briefing = orchestrator.generate_briefing(articles_per_feed=1)
    
    print("\n" + "="*60)
    print("THREAT INTELLIGENCE BRIEFING")
    print("="*60)
    
    new_count = db.save_briefing_run(briefing['briefs'])
    
    for i, brief in enumerate(briefing['briefs'], 1):
        print(f"\n{i}. {brief['title']}")
        print(f"   Impact: {brief['pentester_impact']}")
        
        if brief['mitre_techniques']:
            techs = ", ".join(brief['mitre_techniques'])
            print(f"   MITRE: {techs}")
        
        print(f"   🎯 ACTION: {brief['tactical_takeaway']}")
        print(f"   Link: {brief['link']}")
    
    stats = db.get_stats()
    print(f"\n[DB] {new_count} new articles saved. Total: {stats['total']}")