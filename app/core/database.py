import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import DATA_DIR


class BriefingDB:
    """Simple SQLite storage for threat briefings"""
    
    def __init__(self):
        self.db_path = DATA_DIR / "briefings.db"
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS briefings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    source TEXT,
                    published TEXT,
                    summary TEXT,
                    vulnerability TEXT,
                    affected TEXT,
                    pentester_impact TEXT,
                    whats_happening TEXT DEFAULT '',
                    mitre_techniques TEXT,
                    tactical_takeaway TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Add column if upgrading from old schema
            try:
                conn.execute("ALTER TABLE briefings ADD COLUMN whats_happening TEXT DEFAULT ''")
            except:
                pass  # Column already exists
            conn.commit()
    
    def save_brief(self, brief: dict) -> bool:
        """Save a single briefing. Returns False if already exists (duplicate link)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO briefings 
                    (title, link, source, published, summary, vulnerability, 
                     affected, pentester_impact, whats_happening, mitre_techniques, tactical_takeaway)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    brief['title'],
                    brief['link'],
                    brief.get('source', ''),
                    brief.get('published', ''),
                    brief.get('summary', ''),
                    brief.get('vulnerability', ''),
                    brief.get('affected', ''),
                    brief.get('pentester_impact', ''),
                    brief.get('whats_happening', ''),
                    json.dumps(brief.get('mitre_techniques', [])),
                    brief.get('tactical_takeaway', '')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"  DB Error: {e}")
            return False
    
    def save_briefing_run(self, briefs: list) -> int:
        """Save all briefs from a run. Returns count of new articles saved."""
        new_count = 0
        for brief in briefs:
            if self.save_brief(brief):
                new_count += 1
        return new_count
    
    def get_recent(self, limit: int = 10) -> list:
        """Get most recent briefings"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM briefings ORDER BY fetched_at DESC LIMIT ?", 
                (limit,)
            ).fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def search(self, query: str, limit: int = 10) -> list:
        """Full-text search across title, summary, vulnerability, techniques"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM briefings 
                WHERE title LIKE ? 
                   OR summary LIKE ? 
                   OR vulnerability LIKE ? 
                   OR mitre_techniques LIKE ?
                ORDER BY fetched_at DESC 
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit)).fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_stats(self) -> dict:
        """Quick stats for dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM briefings").fetchone()[0]
            recent = conn.execute(
                "SELECT COUNT(*) FROM briefings WHERE fetched_at > datetime('now', '-7 days')"
            ).fetchone()[0]
        
        return {"total": total, "last_7_days": recent}
    
    def _row_to_dict(self, row) -> dict:
        """Convert SQLite row to dict, parsing JSON fields"""
        brief = dict(row)
        try:
            brief['mitre_techniques'] = json.loads(brief.get('mitre_techniques', '[]'))
        except (json.JSONDecodeError, TypeError):
            brief['mitre_techniques'] = []
        return brief


if __name__ == "__main__":
    # Test the database
    db = BriefingDB()
    
    # Test save
    test_brief = {
        "title": "Test: New CVE-2026-12345 Exploit",
        "link": "https://example.com/test-article",
        "source": "test_feed",
        "summary": "Test article for DB validation",
        "vulnerability": "Buffer overflow",
        "affected": "Test software v1.0",
        "pentester_impact": "Can be used for initial access",
        "mitre_techniques": ["T1190", "T1203"],
        "tactical_takeaway": "nuclei -t cve/2026/CVE-2026-12345.yaml -l targets.txt"
    }
    
    db.save_brief(test_brief)
    
    # Test read
    print("[*] Recent briefings:")
    for brief in db.get_recent(3):
        print(f"  {brief['title']}")
        print(f"  Techniques: {brief['mitre_techniques']}")
        print()
    
    # Test search
    print("[*] Search 'buffer':")
    for brief in db.search("buffer"):
        print(f"  {brief['title']}")
    
    # Test stats
    stats = db.get_stats()
    print(f"\n[*] Stats: {stats}")
