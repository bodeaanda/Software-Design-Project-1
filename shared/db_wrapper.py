import sqlite3
import time
from shared.app_config import AppConfig

class DatabaseWrapper:
    def __init__(self, config: AppConfig):
        self._db_path = config.db_path
        self._conn = sqlite3.connect(self._db_path)
        self._create_schema()

    def _create_schema(self):
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id        INTEGER PRIMARY KEY,
                path      TEXT UNIQUE NOT NULL,
                extension TEXT,
                size      INTEGER,
                mtime     REAL,
                preview   TEXT,
                score     REAL DEFAULT 0.0
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

    def upsert_file(self, path, extension, size, mtime, preview, score=0.0):
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO files (path, extension, size, mtime, preview, score)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                extension=excluded.extension,
                size=excluded.size,
                mtime=excluded.mtime,
                preview=excluded.preview,
                score=excluded.score
        """, (path, extension, size, mtime, preview, score))

        row_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO files_fts (rowid, path, preview)
            VALUES (?, ?, ?)
        """, (row_id, path, preview))

        self._conn.commit()

    def get_mtime(self, path: str) -> float | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT mtime FROM files WHERE path = ?", (path,))
        row = cursor.fetchone()
        return row[0] if row else None

    def search(self, parsed: dict) -> list[dict]:
        cursor = self._conn.cursor()
        conditions = []
        params = []

        for term in parsed.get("path", []):
            conditions.append("f.path LIKE ?")
            params.append(f"%{term}%")

        for term in parsed.get("content", []):
            conditions.append("f.preview LIKE ?")
            params.append(f"%{term}%")

        for term in parsed.get("general", []):
            conditions.append("(f.path LIKE ? OR f.preview LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%"])

        if not conditions:
            return []

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT f.path, f.extension, f.preview, f.score, f.mtime
            FROM files f
            WHERE {where_clause}
            ORDER BY f.score DESC
            LIMIT 20
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [{"path": r[0], "extension": r[1], "preview": r[2], "score": r[3], "mtime": r[4]} for r in rows]

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

    def close(self):
        self._conn.close()