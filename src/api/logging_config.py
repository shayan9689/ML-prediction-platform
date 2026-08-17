"""JSON-lines request logging plus optional Supabase/SQLite persistence."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import ROOT

LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"
SQLITE_PATH = LOG_DIR / "predictions.db"

logger = logging.getLogger("ml_platform")


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if logger.handlers:
        return
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(stream)


def log_event(event: dict[str, Any]) -> None:
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), **event}
    logger.info(json.dumps(payload, default=str))


def _sqlite() -> sqlite3.Connection:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            task TEXT NOT NULL,
            model_used TEXT,
            input TEXT NOT NULL,
            prediction TEXT NOT NULL,
            latency_ms INTEGER,
            error TEXT
        )
        """
    )
    conn.commit()
    return conn


def persist_prediction(row: dict[str, Any]) -> None:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if url and key:
        try:
            from supabase import create_client

            client = create_client(url, key)
            client.table("prediction_logs").insert(
                {
                    "task": row["task"],
                    "model_used": row.get("model_used"),
                    "input": row.get("input"),
                    "prediction": row.get("prediction"),
                    "latency_ms": row.get("latency_ms"),
                    "error": row.get("error"),
                }
            ).execute()
            return
        except Exception as exc:  # noqa: BLE001
            log_event({"event": "supabase_write_failed", "error": str(exc)})
    conn = _sqlite()
    conn.execute(
        """
        INSERT INTO prediction_logs (created_at, task, model_used, input, prediction, latency_ms, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            row["task"],
            row.get("model_used"),
            json.dumps(row.get("input"), default=str),
            json.dumps(row.get("prediction"), default=str),
            row.get("latency_ms"),
            row.get("error"),
        ),
    )
    conn.commit()
    conn.close()
