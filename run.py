#!/usr/bin/env python3
"""
Threat Intelligence Briefing - CLI Runner
Usage:
    python3 run.py              # Full briefing
    python3 run.py --quick      # 1 article per feed (faster)
    python3 run.py --history    # Last 10 saved briefings
    python3 run.py --search aws # Search for keyword
    python3 run.py --stats      # Database stats
"""

import sys
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from agents.orchestrator import ThreatOrchestrator
from core.database import BriefingDB


def print_brief(brief: dict, index: int = 1):
    """Pretty print a single briefing"""
    priority = brief.get('priority', 'LOW')
    emoji = "🔴" if priority == "HIGH" else "🟡"
    matched = brief.get('matched_tech', [])
    
    print(f"\n{index}. {emoji} {brief['title']}")
    print(f"   📅 {brief.get('fetched_at', brief.get('published', 'Unknown date'))}")
    
    if matched:
        print(f"   📌 MATCHES YOUR STACK: {', '.join(matched)}")
    
    if brief.get('whats_happening'):
        print(f"   📖 WHAT'S HAPPENING: {brief['whats_happening']}")
    
    print(f"   💥 IMPACT: {brief['pentester_impact']}")
    
    if brief.get('mitre_techniques'):
        techs = ", ".join(brief['mitre_techniques'])
        print(f"   🔖 MITRE: {techs}")
    
    print(f"   🎯 ACTION: {brief['tactical_takeaway']}")
    print(f"   🔗 {brief['link']}")


def cmd_full(args):
    """Run full briefing pipeline"""
    print("=" * 60)
    print("THREAT INTELLIGENCE BRIEFING")
    print("=" * 60)
    
    orchestrator = ThreatOrchestrator()
    db = BriefingDB()
    
    briefing = orchestrator.generate_briefing(articles_per_feed=args.per_feed)
    
    if "error" in briefing:
        print(f"\n[!] {briefing['error']}")
        return
    
    new_count = db.save_briefing_run(briefing['briefs'])
    
    for i, brief in enumerate(briefing['briefs'], 1):
        print_brief(brief, i)
    
    stats = db.get_stats()
    print(f"\n{'=' * 60}")
    print(f"Saved: {new_count} new | Total in DB: {stats['total']}")
    print(f"{'=' * 60}")


def cmd_history(args):
    """Show recent briefings from database"""
    db = BriefingDB()
    briefs = db.get_recent(limit=args.limit)
    
    print("=" * 60)
    print(f"LAST {len(briefs)} BRIEFINGS")
    print("=" * 60)
    
    if not briefs:
        print("\nNo briefings saved yet. Run without --history to fetch new ones.")
        return
    
    for i, brief in enumerate(briefs, 1):
        print_brief(brief, i)


def cmd_search(args):
    """Search saved briefings"""
    db = BriefingDB()
    briefs = db.search(args.query, limit=args.limit)
    
    print("=" * 60)
    print(f'SEARCH: "{args.query}" - {len(briefs)} RESULTS')
    print("=" * 60)
    
    if not briefs:
        print("\nNo matches found.")
        return
    
    for i, brief in enumerate(briefs, 1):
        print_brief(brief, i)


def cmd_stats(args):
    """Show database statistics"""
    db = BriefingDB()
    stats = db.get_stats()
    
    print("=" * 60)
    print("DATABASE STATS")
    print("=" * 60)
    print(f"  Total briefings:    {stats['total']}")
    print(f"  Last 7 days:        {stats['last_7_days']}")


def main():
    parser = argparse.ArgumentParser(
        description="Threat Intelligence Briefing - Pentester-focused security news"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Full briefing
    full_parser = subparsers.add_parser("full", help="Run full briefing pipeline")
    full_parser.add_argument("--per-feed", type=int, default=1, 
                            help="Articles per feed (default: 1)")
    full_parser.set_defaults(func=cmd_full)
    
    # Quick briefing (alias)
    quick_parser = subparsers.add_parser("quick", help="Quick briefing (alias for full --per-feed 1)")
    quick_parser.set_defaults(func=lambda a: cmd_full(argparse.Namespace(per_feed=1)))
    
    # History
    hist_parser = subparsers.add_parser("history", help="View saved briefings")
    hist_parser.add_argument("--limit", type=int, default=10, 
                            help="Number to show (default: 10)")
    hist_parser.set_defaults(func=cmd_history)
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search saved briefings")
    search_parser.add_argument("query", help="Search term")
    search_parser.add_argument("--limit", type=int, default=10,
                              help="Max results (default: 10)")
    search_parser.set_defaults(func=cmd_search)
    
    # Stats
    stats_parser = subparsers.add_parser("stats", help="Database statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if args.command is None:
        # Default: run full briefing
        cmd_full(argparse.Namespace(per_feed=1))
    else:
        args.func(args)


if __name__ == "__main__":
    main()
