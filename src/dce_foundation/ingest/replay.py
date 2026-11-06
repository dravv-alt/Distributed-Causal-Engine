"""CLI for receipt-order inspection of the local durable intake log."""
from __future__ import annotations

import argparse
import json

from .otlp import replay_evidence
from .store import IntakeStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay DCE OTLP intake batches in durable receipt order")
    parser.add_argument("--database", default="data/raw/intake/dce-intake.sqlite3")
    parser.add_argument("--after-sequence", default=0, type=int)
    args = parser.parse_args()
    store = IntakeStore(args.database)
    store.initialize()
    for batch in store.replay(args.after_sequence, include_payload=True):
        print(json.dumps({
            "sequence": batch.sequence, "signal": batch.signal, "received_at": batch.received_at,
            "payload_sha256": batch.payload_sha256, "duplicate_of_sequence": batch.duplicate_of_sequence,
            "source_identities": batch.source_identities, "event_time_min_unix_nano": batch.event_time_min_unix_nano,
            "event_time_max_unix_nano": batch.event_time_max_unix_nano, "item_count": batch.item_count,
            "resource_count": batch.resource_count, "summary": batch.summary,
            "evidence": replay_evidence(batch.signal, batch.payload),
        }, sort_keys=True))


if __name__ == "__main__":
    main()
