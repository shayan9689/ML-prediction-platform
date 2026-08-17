"""Sync saved metrics JSON into Supabase model_metrics table."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.config import ARTIFACTS, TASKS


def sync_model_metrics_to_supabase(artifacts_dir: Path | None = None) -> dict:
    """Upsert one row per task into Supabase. No-op if env vars missing."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return {"synced": 0, "skipped": "SUPABASE_URL or SERVICE_ROLE_KEY not set"}

    folder = artifacts_dir or ARTIFACTS
    try:
        from supabase import create_client
    except ImportError:
        return {"synced": 0, "error": "supabase package not installed"}

    client = create_client(url, key)
    synced = 0
    for task_id in TASKS:
        meta_path = folder / f"{task_id}_metrics.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        row = {
            "task": task_id,
            "best_model": meta.get("best_model", "unknown"),
            "metrics": meta.get("metrics", {}),
            "comparison": meta.get("comparison", []),
            "feature_importance": meta.get("feature_importance", []),
            "trained_at": meta.get("trained_at") or datetime.now(timezone.utc).isoformat(),
        }
        client.table("model_metrics").upsert(row).execute()
        synced += 1
    return {"synced": synced}
