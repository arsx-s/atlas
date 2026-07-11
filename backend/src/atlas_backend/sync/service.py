"""Cloud sync service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from atlas_backend.persistence import AtlasLocalStore


class SyncService:
    def __init__(self, store: AtlasLocalStore) -> None:
        self.store = store

    def enqueue(self, entity_type: str, entity_id: str, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "sync_id": str(uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "operation": operation,
            "payload": json.dumps(payload),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.store.enqueue_sync(record)
        return record

    def list_pending(self) -> list[dict[str, Any]]:
        return self.store.list_pending_syncs()

    def resolve(self, sync_id: str, status: str) -> None:
        self.store.mark_sync_status(sync_id, status)

