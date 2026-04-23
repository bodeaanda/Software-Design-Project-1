import sqlite3

from fastapi import params
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
                preview   TEXT
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
            USING fts5(path, preview, content='files', content_rowid='id');
        """)
        self._conn.commit()

    def upsert_file(self, path, extension, size, mtime, preview):
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO files (path, extension, size, mtime, preview)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                extension=excluded.extension,
                size=excluded.size,
                mtime=excluded.mtime,
                preview=excluded.preview
        """, (path, extension, size, mtime, preview))

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
        SELECT f.path, f.extension, f.preview
        FROM files f
        WHERE {where_clause}
        LIMIT 20
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [{"path": r[0], "extension": r[1], "preview": r[2]} for r in rows]

    def close(self):
        self._conn.close()