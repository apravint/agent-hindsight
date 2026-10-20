import os
import time
import math
import re
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB_DIR = os.path.expanduser("~/.local/share/hindsight")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "memory.db")

class HindsightStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("HINDSIGHT_DB_PATH") or DEFAULT_DB_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 5,
                access_count INTEGER DEFAULT 0,
                created_at REAL,
                last_accessed REAL
            );
            """)
            cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                fact,
                category UNINDEXED,
                content='memories',
                content_rowid='id'
            );
            """)
            cur.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
              INSERT INTO memories_fts(rowid, fact, category) VALUES (new.id, new.fact, new.category);
            END;
            """)
            cur.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
              INSERT INTO memories_fts(memories_fts, rowid, fact, category) VALUES('delete', old.id, old.fact, old.category);
            END;
            """)
            conn.commit()

    def retain(self, fact: str, category: str = "general", importance: int = 5) -> Dict[str, Any]:
        """Retain a fact with explicit importance rating (1-10)."""
        now = time.time()
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO memories (fact, category, importance, access_count, created_at, last_accessed) VALUES (?, ?, ?, 1, ?, ?)",
                (fact.strip(), category.lower(), importance, now, now)
            )
            conn.commit()
            mem_id = cur.lastrowid
        return {"ok": True, "id": mem_id, "fact": fact, "category": category, "importance": importance}

    def recall(self, query: str = "", category: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Recalls facts ranked by BM25 match, explicit importance, and exponential recency decay."""
        now = time.time()
        query_clean = query.strip()

        with self.get_connection() as conn:
            cur = conn.cursor()
            if query_clean:
                words = re.findall(r'[a-zA-Z0-9_]+', query_clean)
                terms = [f'"{w}"' for w in words if len(w) > 1]
                fts_query = " OR ".join(terms) if terms else f'"{query_clean}"'
                sql = """
                SELECT m.id, m.fact, m.category, m.importance, m.access_count, m.created_at, m.last_accessed, bm25(memories_fts) as bm25_score
                FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                """
                params = [fts_query]
                if category:
                    sql += " AND m.category = ?"
                    params.append(category.lower())
            else:
                sql = "SELECT id, fact, category, importance, access_count, created_at, last_accessed, 0.0 as bm25_score FROM memories"
                params = []
                if category:
                    sql += " WHERE category = ?"
                    params.append(category.lower())

            cur.execute(sql, params)
            rows = cur.fetchall()

            scored = []
            for r in rows:
                m_id, fact, cat, importance, acc_count, created_at, last_acc, bm25 = r
                age_hours = (now - last_acc) / 3600.0
                # Exponential recency decay
                decay = math.exp(-0.005 * age_hours)
                total_score = (abs(bm25) * 1.5 if bm25 != 0 else 1.0) * (importance / 5.0) * decay
                scored.append({
                    "id": m_id,
                    "fact": fact,
                    "category": cat,
                    "importance": importance,
                    "created_at": datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M"),
                    "score": round(total_score, 3)
                })

            scored.sort(key=lambda x: x["score"], reverse=True)
            results = scored[:limit]

            for item in results:
                cur.execute("UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id = ?", (now, item["id"]))
            conn.commit()

        return results

    def reflect(self) -> Dict[str, Any]:
        """Synthesizes memory statistics and thematic anchors."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), AVG(importance), COUNT(DISTINCT category) FROM memories")
            total, avg_imp, distinct_cats = cur.fetchone()
            
            cur.execute("SELECT category, COUNT(*) FROM memories GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5")
            cat_counts = cur.fetchall()

            cur.execute("SELECT id, fact, importance, access_count FROM memories ORDER BY importance DESC, access_count DESC LIMIT 5")
            top_memories = cur.fetchall()

        return {
            "ok": True,
            "total_memories": total or 0,
            "avg_importance": round(avg_imp or 0, 1),
            "categories_count": distinct_cats or 0,
            "top_categories": [{"category": c, "count": count} for c, count in cat_counts],
            "top_anchors": [{"id": m[0], "fact": m[1], "importance": m[2], "accesses": m[3]} for m in top_memories]
        }

# Global singleton functions
_default_store = None

def get_store() -> HindsightStore:
    global _default_store
    if _default_store is None:
        _default_store = HindsightStore()
    return _default_store

def init_db(db_path: Optional[str] = None):
    return HindsightStore(db_path)

def retain(fact: str, category: str = "general", importance: int = 5):
    return get_store().retain(fact, category, importance)

def recall(query: str = "", category: str = "", limit: int = 10):
    return get_store().recall(query, category, limit)

def reflect():
    return get_store().reflect()
