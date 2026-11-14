from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS trends (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT,
  source TEXT,
  source_url TEXT UNIQUE,
  region TEXT,
  fetched_at TEXT NOT NULL,
  raw_json TEXT
);
CREATE TABLE IF NOT EXISTS story_ideas (
  id TEXT PRIMARY KEY,
  trend_id TEXT REFERENCES trends(id),
  title TEXT NOT NULL,
  angle TEXT,
  category TEXT,
  scores_json TEXT,
  score REAL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'new',   -- new|selected|drafted|rejected|exhausted
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS drafts (
  id TEXT PRIMARY KEY,
  idea_id TEXT REFERENCES story_ideas(id),
  slug TEXT UNIQUE,
  path TEXT,
  version INTEGER DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'written', -- written|comedy_ok|comedy_fail|safety_ok|safety_fail|approved|published|rejected
  comedy_score REAL,
  safety_score REAL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  draft_id TEXT REFERENCES drafts(id),
  reviewer TEXT NOT NULL,               -- comedy_editor|safety_editor|seo_editor
  verdict TEXT NOT NULL,                -- pass|rewrite|fail
  score REAL,
  notes TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS published (
  id TEXT PRIMARY KEY,
  draft_id TEXT REFERENCES drafts(id),
  slug TEXT UNIQUE NOT NULL,
  url TEXT,
  commit_sha TEXT,
  deployed INTEGER DEFAULT 0,
  published_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS social_assets (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL,
  platform TEXT NOT NULL,
  kind TEXT NOT NULL,                   -- post|caption|script|graphic|alt_headline
  path TEXT,
  content TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metrics (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  value REAL,
  dims_json TEXT,
  recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY,
  agent TEXT NOT NULL,
  status TEXT NOT NULL,                 -- running|ok|error
  detail TEXT,
  started_at TEXT NOT NULL,
  ended_at TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  payload_json TEXT,
  status TEXT NOT NULL DEFAULT 'pending', -- pending|done|error|dead
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS subscribers (
  email TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'subscribed', -- subscribed|unsubscribed
  updated_at TEXT NOT NULL
);
"""


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def uid() -> str:
    return uuid.uuid4().hex[:12]


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def run(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    with connect() as conn:
        return conn.execute(sql, params)


def query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def one(sql: str, params: tuple = ()) -> dict[str, Any] | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def log_run(agent: str, detail: str = "") -> str:
    rid = uid()
    run(
        "INSERT INTO agent_runs (id, agent, status, detail, started_at) VALUES (?,?,?,?,?)",
        (rid, agent, "running", detail, now()),
    )
    return rid


def finish_run(rid: str, status: str = "ok", detail: str = "") -> None:
    run(
        "UPDATE agent_runs SET status=?, detail=?, ended_at=? WHERE id=?",
        (status, detail, now(), rid),
    )


def enqueue(kind: str, payload: dict[str, Any]) -> str:
    tid = uid()
    run(
        "INSERT INTO tasks (id, kind, payload_json, created_at, updated_at) VALUES (?,?,?,?,?)",
        (tid, kind, json.dumps(payload), now(), now()),
    )
    return tid


def dequeue(kind: str) -> dict[str, Any] | None:
    row = one(
        "SELECT * FROM tasks WHERE kind=? AND status='pending' ORDER BY created_at LIMIT 1",
        (kind,),
    )
    return row


def task_done(tid: str) -> None:
    run("UPDATE tasks SET status='done', updated_at=? WHERE id=?", (now(), tid))


def task_error(tid: str, error: str) -> None:
    run(
        """UPDATE tasks SET attempts=attempts+1, last_error=?, updated_at=?,
           status=CASE WHEN attempts+1>=max_attempts THEN 'dead' ELSE 'pending' END
           WHERE id=?""",
        (error, now(), tid),
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
