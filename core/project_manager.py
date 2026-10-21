"""
PharmaLeaf AI - Project and History Manager
Local SQLite database persistence for saving, loading, and tracking leaflet projects.
"""
import os
import json
import sqlite3
import datetime
from typing import Any
from .constants import DATABASE_PATH, USER_APPDATA_DIR


class ProjectManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes SQLite schema for projects and document history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    source_file TEXT,
                    page_count INTEGER DEFAULT 1,
                    is_arabic INTEGER DEFAULT 1,
                    columns_count INTEGER DEFAULT 1,
                    data_json TEXT NOT NULL,
                    plain_text TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC)
            """)
            conn.commit()

    def save_project(
        self,
        name: str,
        source_file: str,
        doc_data: dict[str, Any],
        project_id: int | None = None
    ) -> int:
        """
        Saves or updates a project record in the local SQLite database.
        """
        now = datetime.datetime.now().isoformat()
        columns_count = doc_data.get("columns_count", 1)
        is_arabic = 1 if doc_data.get("is_arabic", True) else 0
        plain_text = doc_data.get("ordered_text", "")
        data_json = json.dumps(doc_data, ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if project_id:
                cursor.execute("""
                    UPDATE projects
                    SET name = ?, source_file = ?, is_arabic = ?, columns_count = ?,
                        data_json = ?, plain_text = ?, updated_at = ?
                    WHERE id = ?
                """, (name, source_file, is_arabic, columns_count, data_json, plain_text, now, project_id))
                return project_id
            else:
                cursor.execute("""
                    INSERT INTO projects (
                        name, source_file, page_count, is_arabic, columns_count,
                        data_json, plain_text, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, source_file, 1, is_arabic, columns_count, data_json, plain_text, now, now))
                conn.commit()
                return cursor.lastrowid

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        """Retrieves a single project by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "source_file": row["source_file"],
                "page_count": row["page_count"],
                "is_arabic": bool(row["is_arabic"]),
                "columns_count": row["columns_count"],
                "doc_data": json.loads(row["data_json"]),
                "plain_text": row["plain_text"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }

    def list_recent_projects(self, limit: int = 30) -> list[dict[str, Any]]:
        """Lists recent projects ordered by last update date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, source_file, page_count, is_arabic, columns_count,
                       length(plain_text) as char_count, created_at, updated_at
                FROM projects
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_project(self, project_id: int) -> bool:
        """Deletes a project by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0
