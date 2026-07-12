"""SQLite-backed local persistence."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass(slots=True)
class StoredRecord:
    id: str
    payload: dict[str, Any]


class AtlasLocalStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    display_name TEXT,
                    email_verified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    refresh_token TEXT,
                    revoked INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS sync_queue (
                    sync_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entities (
                    entity_key TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS collections (
                    collection_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    icon TEXT DEFAULT '',
                    color TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS notes (
                    note_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    is_pinned INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS tags (
                    tag_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT DEFAULT '',
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS saved_research (
                    saved_research_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    research_session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS timeline_events (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_format TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL DEFAULT 0,
                    storage_path TEXT NOT NULL,
                    page_count INTEGER DEFAULT 0,
                    author TEXT DEFAULT '',
                    chunk_count INTEGER DEFAULT 0,
                    indexed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    page_number INTEGER,
                    section TEXT DEFAULT '',
                    start_char INTEGER DEFAULT 0,
                    end_char INTEGER DEFAULT 0,
                    embedding BLOB,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS research_sessions (
                    session_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    query TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending',
                    model_used TEXT DEFAULT 'gpt-4',
                    total_tasks INTEGER DEFAULT 0,
                    completed_tasks INTEGER DEFAULT 0,
                    failed_tasks INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    messages TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS research_evidence (
                    evidence_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_url TEXT,
                    source_document TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    tags TEXT DEFAULT '[]',
                    collected_by_task TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES research_sessions(session_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS research_reports (
                    report_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    executive_summary TEXT DEFAULT '',
                    sections TEXT DEFAULT '[]',
                    supporting_evidence TEXT DEFAULT '[]',
                    citations TEXT DEFAULT '[]',
                    markdown_content TEXT DEFAULT '',
                    generated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
                CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
                CREATE INDEX IF NOT EXISTS idx_research_sessions_project ON research_sessions(project_id);
                CREATE INDEX IF NOT EXISTS idx_research_sessions_user ON research_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_evidence_session ON research_evidence(session_id);
            """)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- Users ---
    def upsert_user(self, user: dict[str, Any]) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("""
                INSERT INTO users (user_id, email, password_hash, display_name, email_verified, created_at, updated_at)
                VALUES (:user_id, :email, :password_hash, :display_name, :email_verified, :created_at, :updated_at)
                ON CONFLICT(user_id) DO UPDATE SET
                    email=excluded.email, password_hash=excluded.password_hash,
                    display_name=excluded.display_name, email_verified=excluded.email_verified,
                    updated_at=excluded.updated_at
            """, user)

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    # --- Devices ---
    def upsert_device(self, device: dict[str, Any]) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("""
                INSERT INTO devices (device_id, user_id, name, last_seen_at, refresh_token, revoked)
                VALUES (:device_id, :user_id, :name, :last_seen_at, :refresh_token, :revoked)
                ON CONFLICT(device_id) DO UPDATE SET
                    user_id=excluded.user_id, name=excluded.name,
                    last_seen_at=excluded.last_seen_at, refresh_token=excluded.refresh_token,
                    revoked=excluded.revoked
            """, device)

    # --- Auth Sessions ---
    def upsert_session(self, session: dict[str, Any]) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("""
                INSERT INTO auth_sessions (session_id, user_id, device_id, access_token, refresh_token, expires_at, revoked, created_at)
                VALUES (:session_id, :user_id, :device_id, :access_token, :refresh_token, :expires_at, :revoked, :created_at)
                ON CONFLICT(session_id) DO UPDATE SET
                    access_token=excluded.access_token, refresh_token=excluded.refresh_token,
                    expires_at=excluded.expires_at, revoked=excluded.revoked
            """, session)

    def get_session_by_refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM auth_sessions WHERE refresh_token = ?", (refresh_token,)).fetchone()
            return dict(row) if row else None

    def revoke_session(self, session_id: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("UPDATE auth_sessions SET revoked = 1 WHERE session_id = ?", (session_id,))

    # --- Sync ---
    def enqueue_sync(self, sync_item: dict[str, Any]) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("""
                INSERT INTO sync_queue (sync_id, entity_type, entity_id, operation, payload, status, created_at, updated_at)
                VALUES (:sync_id, :entity_type, :entity_id, :operation, :payload, :status, :created_at, :updated_at)
                ON CONFLICT(sync_id) DO UPDATE SET
                    status=excluded.status, payload=excluded.payload, updated_at=excluded.updated_at
            """, sync_item)

    def list_pending_syncs(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY created_at ASC").fetchall()
            return [dict(row) for row in rows]

    def mark_sync_status(self, sync_id: str, status: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("UPDATE sync_queue SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE sync_id = ?", (status, sync_id))

    # --- Entities (generic key-value) ---
    def upsert_entity(self, entity_key: str, entity_type: str, payload: dict[str, Any], updated_at: str = "") -> None:
        with self._lock, self._connect() as connection:
            connection.execute("""
                INSERT INTO entities (entity_key, entity_type, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(entity_key) DO UPDATE SET
                    entity_type=excluded.entity_type, payload=excluded.payload, updated_at=excluded.updated_at
            """, (entity_key, entity_type, json.dumps(payload), updated_at or self._now()))

    def get_entity(self, entity_key: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM entities WHERE entity_key = ?", (entity_key,)).fetchone()
            if not row: return None
            return {"entity_key": row["entity_key"], "entity_type": row["entity_type"],
                    "payload": json.loads(row["payload"]), "updated_at": row["updated_at"]}

    # --- Projects ---
    def create_project(self, project: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO projects (project_id, user_id, name, description, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project["project_id"], project["user_id"], project["name"],
                  project.get("description", ""), json.dumps(project.get("tags", [])), now, now))
            return project["project_id"]

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if not row: return None
            return {**dict(row), "tags": json.loads(row["tags"]) if row["tags"] else []}

    def list_projects(self, user_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)).fetchall()
            return [{**dict(r), "tags": json.loads(r["tags"]) if r["tags"] else []} for r in rows]

    def update_project(self, project_id: str, updates: dict[str, Any]) -> bool:
        with self._lock, self._connect() as connection:
            now = self._now()
            fields = []
            vals = []
            for key in ("name", "description"):
                if key in updates:
                    fields.append(f"{key} = ?")
                    vals.append(updates[key])
            if "tags" in updates:
                fields.append("tags = ?")
                vals.append(json.dumps(updates["tags"]))
            if not fields: return False
            fields.append("updated_at = ?")
            vals.append(now)
            vals.append(project_id)
            cursor = connection.execute(f"UPDATE projects SET {', '.join(fields)} WHERE project_id = ?", vals)
            return cursor.rowcount > 0

    def delete_project(self, project_id: str) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            return cursor.rowcount > 0

    # --- Notes ---
    def create_note(self, note: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO notes (note_id, project_id, title, content, tags, is_pinned, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (note["note_id"], note["project_id"], note["title"], note.get("content", ""),
                  json.dumps(note.get("tags", [])), note.get("is_pinned", 0), now, now))
            return note["note_id"]

    def list_notes(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM notes WHERE project_id = ? ORDER BY updated_at DESC", (project_id,)).fetchall()
            return [{**dict(r), "tags": json.loads(r["tags"]) if r["tags"] else []} for r in rows]

    # --- Saved Research ---
    def save_research(self, saved: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO saved_research (saved_research_id, project_id, research_session_id, title, summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (saved["saved_research_id"], saved["project_id"], saved["research_session_id"],
                  saved["title"], saved.get("summary", ""), now))
            return saved["saved_research_id"]

    def list_saved_research(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM saved_research WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
            return [dict(r) for r in rows]

    # --- Timeline ---
    def record_timeline_event(self, event: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO timeline_events (event_id, project_id, event_type, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (event["event_id"], event["project_id"], event["event_type"], event["description"], now))
            return event["event_id"]

    def get_timeline(self, project_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM timeline_events WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
                (project_id, limit)).fetchall()
            return [dict(r) for r in rows]

    # --- Documents ---
    def create_document(self, doc: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO documents (document_id, project_id, title, file_name, file_format, file_size_bytes,
                    storage_path, page_count, author, chunk_count, indexed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc["document_id"], doc["project_id"], doc["title"], doc["file_name"],
                  doc["file_format"], doc["file_size_bytes"], doc.get("storage_path", ""),
                  doc.get("page_count", 0), doc.get("author", ""), doc.get("chunk_count", 0),
                  doc.get("indexed", 0), now, now))
            return doc["document_id"]

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,)).fetchone()
            return dict(row) if row else None

    def list_documents(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM documents WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
            return [dict(r) for r in rows]

    def delete_document(self, document_id: str) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            return cursor.rowcount > 0

    # --- Document Chunks ---
    def save_chunks(self, chunks: list[dict[str, Any]]) -> None:
        with self._lock, self._connect() as connection:
            now = self._now()
            for c in chunks:
                connection.execute("""
                    INSERT INTO document_chunks (chunk_id, document_id, content, page_number, section, start_char, end_char, embedding, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (c["chunk_id"], c["document_id"], c["content"], c.get("page_number"),
                      c.get("section", ""), c.get("start_char", 0), c.get("end_char", 0),
                      json.dumps(c.get("embedding", [])) if c.get("embedding") else None, now))

    def search_chunks(self, query_embedding: list[float] | None = None, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM document_chunks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # --- Research Sessions ---
    def create_research_session(self, session: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO research_sessions (session_id, project_id, user_id, title, query, description,
                    status, model_used, total_tasks, completed_tasks, failed_tasks, total_cost, messages, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session["session_id"], session["project_id"], session["user_id"],
                  session["title"], session["query"], session.get("description", ""),
                  session.get("status", "pending"), session.get("model_used", "gpt-4"),
                  session.get("total_tasks", 0), session.get("completed_tasks", 0),
                  session.get("failed_tasks", 0), session.get("total_cost", 0.0),
                  json.dumps(session.get("messages", [])), now))
            return session["session_id"]

    def get_research_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM research_sessions WHERE session_id = ?", (session_id,)).fetchone()
            if not row: return None
            result = dict(row)
            result["messages"] = json.loads(result["messages"]) if result["messages"] else []
            return result

    def list_research_sessions(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM research_sessions WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["messages"] = json.loads(d["messages"]) if d["messages"] else []
                result.append(d)
            return result

    def update_research_session(self, session_id: str, updates: dict[str, Any]) -> bool:
        with self._lock, self._connect() as connection:
            fields = []
            vals = []
            for key in ("status", "title", "query", "description", "model_used", "total_tasks",
                        "completed_tasks", "failed_tasks", "total_cost"):
                if key in updates:
                    fields.append(f"{key} = ?")
                    vals.append(updates[key])
            if "messages" in updates:
                fields.append("messages = ?")
                vals.append(json.dumps(updates["messages"]))
            if "started_at" in updates:
                fields.append("started_at = ?")
                vals.append(updates["started_at"])
            if "completed_at" in updates:
                fields.append("completed_at = ?")
                vals.append(updates["completed_at"])
            if not fields: return False
            vals.append(session_id)
            cursor = connection.execute(f"UPDATE research_sessions SET {', '.join(fields)} WHERE session_id = ?", vals)
            return cursor.rowcount > 0

    # --- Research Evidence ---
    def save_evidence(self, evidence: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO research_evidence (evidence_id, session_id, evidence_type, title, content,
                    source_url, source_document, confidence_score, tags, collected_by_task, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (evidence["evidence_id"], evidence["session_id"], evidence["evidence_type"],
                  evidence["title"], evidence["content"], evidence.get("source_url"),
                  evidence.get("source_document"), evidence.get("confidence_score", 1.0),
                  json.dumps(evidence.get("tags", [])), evidence.get("collected_by_task"), now))
            return evidence["evidence_id"]

    def list_evidence(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM research_evidence WHERE session_id = ? ORDER BY created_at DESC", (session_id,)).fetchall()
            return [dict(r) for r in rows]

    # --- Research Reports ---
    def save_report(self, report: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO research_reports (report_id, session_id, title, executive_summary, sections,
                    supporting_evidence, citations, markdown_content, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (report["report_id"], report["session_id"], report["title"],
                  report.get("executive_summary", ""), json.dumps(report.get("sections", [])),
                  json.dumps(report.get("supporting_evidence", [])),
                  json.dumps(report.get("citations", [])),
                  report.get("markdown_content", ""), now))
            return report["report_id"]

    def get_report(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM research_reports WHERE session_id = ? ORDER BY generated_at DESC LIMIT 1",
                (session_id,)).fetchone()
            if not row: return None
            result = dict(row)
            for field in ("sections", "supporting_evidence", "citations"):
                result[field] = json.loads(result[field]) if result[field] else []
            return result

    # --- Settings ---
    def get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as connection:
            row = connection.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,)).fetchone()
            return row["setting_value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=excluded.updated_at
            """, (key, value, now))

    def get_all_settings(self) -> dict[str, str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM settings").fetchall()
            return {r["setting_key"]: r["setting_value"] for r in rows}

    # --- Collections ---
    def create_collection(self, collection: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO collections (collection_id, project_id, name, icon, color, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (collection["collection_id"], collection["project_id"], collection["name"],
                  collection.get("icon", ""), collection.get("color", ""), now))
            return collection["collection_id"]

    def list_collections(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM collections WHERE project_id = ? ORDER BY name", (project_id,)).fetchall()
            return [dict(r) for r in rows]

    # --- Tags ---
    def create_tag(self, tag: dict[str, Any]) -> str:
        with self._lock, self._connect() as connection:
            now = self._now()
            connection.execute("""
                INSERT INTO tags (tag_id, project_id, name, color, usage_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tag["tag_id"], tag["project_id"], tag["name"], tag.get("color", ""),
                  tag.get("usage_count", 0), now))
            return tag["tag_id"]

    def list_tags(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM tags WHERE project_id = ? ORDER BY name", (project_id,)).fetchall()
            return [dict(r) for r in rows]
