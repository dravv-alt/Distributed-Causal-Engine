"""SQLite durable intake log. The primary delivery contract is at-least-once."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Iterator

from .otlp import BatchMetadata


class StoreUnavailable(RuntimeError):
    """A durable commit could not be made; caller must not acknowledge success."""


@dataclass(frozen=True)
class StoredBatch:
    sequence: int
    signal: str
    received_at: str
    payload_sha256: str
    duplicate_of_sequence: int | None
    source_identities: tuple[str, ...]
    event_time_min_unix_nano: int | None
    event_time_max_unix_nano: int | None
    item_count: int
    resource_count: int
    summary: dict
    payload: bytes | None = None


class IntakeStore:
    def __init__(self, path: str | Path, max_database_bytes: int = 128 * 1024 * 1024):
        self.path = Path(path)
        self.max_database_bytes = max_database_bytes

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            yield connection
        except sqlite3.Error as exc:
            raise StoreUnavailable("SQLite storage unavailable") from exc
        finally:
            if "connection" in locals():
                connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS intake_batches (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal TEXT NOT NULL CHECK(signal IN ('metrics', 'traces')),
                    received_at TEXT NOT NULL,
                    payload BLOB NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    source_identities_json TEXT NOT NULL,
                    event_time_min_unix_nano INTEGER,
                    event_time_max_unix_nano INTEGER,
                    item_count INTEGER NOT NULL,
                    resource_count INTEGER NOT NULL,
                    summary_json TEXT NOT NULL,
                    duplicate_of_sequence INTEGER REFERENCES intake_batches(sequence)
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_intake_batches_hash ON intake_batches(payload_sha256)")

    def append(self, metadata: BatchMetadata, payload: bytes) -> StoredBatch:
        if self.path.exists() and self.path.stat().st_size + len(payload) > self.max_database_bytes:
            raise StoreUnavailable("SQLite local storage limit reached")
        received_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connection() as connection:
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute(
                    "SELECT sequence FROM intake_batches WHERE payload_sha256 = ? ORDER BY sequence LIMIT 1", (metadata.payload_sha256,)
                ).fetchone()
                cursor = connection.execute("""
                    INSERT INTO intake_batches (
                        signal, received_at, payload, payload_sha256, source_identities_json,
                        event_time_min_unix_nano, event_time_max_unix_nano, item_count,
                        resource_count, summary_json, duplicate_of_sequence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (metadata.signal, received_at, payload, metadata.payload_sha256,
                      json.dumps(metadata.source_identities), metadata.event_time_min_unix_nano,
                      metadata.event_time_max_unix_nano, metadata.item_count, metadata.resource_count,
                      metadata.summary_json, existing["sequence"] if existing else None))
                sequence = cursor.lastrowid
                connection.execute("COMMIT")
        except sqlite3.Error as exc:
            raise StoreUnavailable("SQLite durable commit failed") from exc
        return StoredBatch(sequence, metadata.signal, received_at, metadata.payload_sha256,
                           existing["sequence"] if existing else None, metadata.source_identities,
                           metadata.event_time_min_unix_nano, metadata.event_time_max_unix_nano,
                           metadata.item_count, metadata.resource_count, json.loads(metadata.summary_json), payload)

    def replay(self, after_sequence: int = 0, include_payload: bool = False) -> list[StoredBatch]:
        with self._connection() as connection:
            rows = connection.execute("""
                SELECT sequence, signal, received_at, payload, payload_sha256, source_identities_json,
                       event_time_min_unix_nano, event_time_max_unix_nano, item_count,
                       resource_count, summary_json, duplicate_of_sequence
                FROM intake_batches WHERE sequence > ? ORDER BY sequence
            """, (after_sequence,)).fetchall()
        return [StoredBatch(row["sequence"], row["signal"], row["received_at"], row["payload_sha256"],
                            row["duplicate_of_sequence"], tuple(json.loads(row["source_identities_json"])),
                            row["event_time_min_unix_nano"], row["event_time_max_unix_nano"], row["item_count"],
                            row["resource_count"], json.loads(row["summary_json"]), row["payload"] if include_payload else None)
                for row in rows]

    def stats(self) -> dict:
        with self._connection() as connection:
            row = connection.execute("""
                SELECT COUNT(*) AS accepted, SUM(CASE WHEN duplicate_of_sequence IS NOT NULL THEN 1 ELSE 0 END) AS duplicates,
                       COALESCE(SUM(LENGTH(payload)), 0) AS payload_bytes, MAX(sequence) AS last_sequence
                FROM intake_batches
            """).fetchone()
        return {"accepted": row["accepted"], "duplicates": row["duplicates"] or 0,
                "payload_bytes": row["payload_bytes"], "last_sequence": row["last_sequence"] or 0,
                "database_path": str(self.path), "database_bytes": self.path.stat().st_size if self.path.exists() else 0,
                "max_database_bytes": self.max_database_bytes}
