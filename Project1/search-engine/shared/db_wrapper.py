import sqlite3
import time
import threading

from shared.levenshtein import levenshtein_distance, similarity_score
from shared.app_config import AppConfig

class DatabaseWrapper:
    def __init__(self, config: AppConfig):
        self._db_path = config.db_path
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._create_schema()

    def _create_schema(self):
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id             INTEGER PRIMARY KEY,
                path           TEXT UNIQUE NOT NULL,
                extension      TEXT,
                size           INTEGER,
                mtime          REAL,
                preview        TEXT,
                score          REAL DEFAULT 0.0,
                dominant_color TEXT,
                file_type      TEXT DEFAULT 'text'
        );

            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
            USING fts5(path, preview, content='files', content_rowid='id');

            CREATE TABLE IF NOT EXISTS search_history (
                id        INTEGER PRIMARY KEY,
                query     TEXT NOT NULL,
                timestamp REAL NOT NULL
            );
        """)
        self._conn.commit()

    def upsert_file(self, path, extension, size, mtime, preview, score=0.0, dominant_color=None, file_type="text"):
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO files (path, extension, size, mtime, preview, score, dominant_color, file_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    extension=excluded.extension,
                    size=excluded.size,
                    mtime=excluded.mtime,
                    preview=excluded.preview,
                    score=excluded.score,
                    dominant_color=excluded.dominant_color,
                    file_type=excluded.file_type
            """, (path, extension, size, mtime, preview, score, dominant_color, file_type))

            row_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO files_fts (rowid, path, preview)
                VALUES (?, ?, ?)
            """, (row_id, path, preview))

            self._conn.commit()

    def get_mtime(self, path: str) -> float | None:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("SELECT mtime FROM files WHERE path = ?", (path,))
            row = cursor.fetchone()
            return row[0] if row else None

    def search(self, parsed: dict) -> list[dict]:
        cursor = self._conn.cursor()
        conditions = []
        params = []

        for term in parsed.get("path", []):
            clean = term.rstrip("*")
            conditions.append("f.path LIKE ?")
            params.append(f"%{clean}%")

        for term in parsed.get("content", []):
            clean = term.rstrip("*")
            conditions.append("f.preview LIKE ?")
            params.append(f"%{clean}%")

        for term in parsed.get("general", []):
            clean = term.rstrip("*")
            conditions.append("(f.path LIKE ? OR f.preview LIKE ?)")
            params.extend([f"%{clean}%", f"%{clean}%"])

        for term in parsed.get("color", []):
            conditions.append("f.dominant_color = ?")
            params.append(term.lower())

        if not conditions:
            return []

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT f.path, f.extension, f.preview, f.score, f.mtime, f.dominant_color, f.file_type
            FROM files f
            WHERE {where_clause}
            ORDER BY f.score DESC
            LIMIT 20
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = [{"path": r[0], "extension": r[1], "preview": r[2], "score": r[3], 
                "mtime": r[4], "dominant_color": r[5], "file_type": r[6]} for r in rows]

        if not results:
            all_terms = parsed.get("general", []) + parsed.get("path", []) + parsed.get("content", [])
            if all_terms:
                #print("[TYPO] No exact results, trying typo search...")
                results = self.typo_search(all_terms)

        return results

    def save_search(self, query: str):
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO search_history (query, timestamp)
            VALUES (?, ?)
        """, (query, time.time()))
        self._conn.commit()

    def get_suggestions(self, prefix: str) -> list[str]:
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT query, COUNT(*) as freq
            FROM search_history
            WHERE query LIKE ?
            GROUP BY query
            ORDER BY freq DESC
            LIMIT 5
        """, (f"{prefix}%",))
        return [row[0] for row in cursor.fetchall()]

    def typo_search(self, query_terms: list[str], threshold: float = 0.5) -> list[dict]:
        from shared.levenshtein import similarity_score

        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT path, extension, preview, score, mtime, dominant_color, file_type
            FROM files
        """)
        all_files = cursor.fetchall()

        results = []
        for row in all_files:
            path = row[0]
            filename = path.split("\\")[-1]
            preview = row[2] if row[2] else ""

            best_score = 0.0
            matched_term = None
            
            for term in query_terms:
                # similarity against filename
                filename_score = similarity_score(term, filename)
                # similarity against preview 
                preview_score = 0.0
                for word in preview.split():
                    word_score = similarity_score(term, word)
                    if word_score > preview_score:
                        preview_score = word_score
                
                # best match between filename and preview
                current_best = max(filename_score, preview_score)
                if current_best > best_score:
                    best_score = current_best
                    matched_term = term

            if best_score >= threshold:
                results.append({
                    "path": row[0],
                    "extension": row[1],
                    "preview": row[2],
                    "score": row[3],
                    "mtime": row[4],
                    "similarity": round(best_score, 2),
                    "dominant_color": row[5],
                    "file_type": row[6],
                })

        results.sort(key=lambda r: (r["similarity"], r["score"]), reverse=True)
        return results[:20]

    def close(self):
        self._conn.close()