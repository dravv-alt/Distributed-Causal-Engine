"""Disk-backed record disposition, provenance and stable event-time replay."""
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sqlite3
from ..domain import canonical_json


@contextmanager
def new_store(path):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    db = sqlite3.connect(path)
    db.executescript('''
        CREATE TABLE sources(source_key TEXT PRIMARY KEY, path TEXT, environment TEXT, header TEXT, profile TEXT);
        CREATE TABLE dispositions(source_key TEXT, source_row INTEGER, state TEXT, error TEXT, raw_json TEXT,
                                  PRIMARY KEY(source_key,source_row));
        CREATE TABLE fingerprints(source_key TEXT, fingerprint TEXT, PRIMARY KEY(source_key,fingerprint));
        CREATE TABLE resources(resource_id TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE observations(oid TEXT PRIMARY KEY,event_ns INTEGER,source_key TEXT,source_row INTEGER,resource_id TEXT,body TEXT);
        CREATE TABLE spans(oid TEXT PRIMARY KEY,environment TEXT,trace_id TEXT,span_id TEXT,parent_id TEXT,
                           resource_id TEXT,event_ns INTEGER,source_key TEXT,source_row INTEGER);
        CREATE TABLE dependencies(did TEXT PRIMARY KEY,event_ns INTEGER,relation_type TEXT,body TEXT);
        CREATE TABLE trace_states(oid TEXT PRIMARY KEY,state TEXT);
    ''')
    try:
        yield db
        db.commit()
    finally:
        db.close()


def add_resource(db, res):
    old = db.execute("SELECT body FROM resources WHERE resource_id=?", (res.resource_id,)).fetchone()
    if old:
        previous = json.loads(old[0])
        # Keep source evidence first seen deterministically; workbook typing upgrades UNKNOWN.
        if previous["resource_kind"] != "UNKNOWN" and previous["resource_kind"] != res.resource_kind:
            if res.resource_kind != "UNKNOWN":
                raise ValueError("conflicting resource kinds")
            return
        if res.resource_kind == "UNKNOWN":
            return
    db.execute("INSERT OR REPLACE INTO resources VALUES (?,?)", (res.resource_id,canonical_json(asdict(res))))


def replay(db):
    for (body,) in db.execute("SELECT body FROM observations ORDER BY event_ns,source_key,source_row,oid"):
        yield json.loads(body)


def canonical_digest(db):
    h = hashlib.sha256()
    for table, order in (("resources","resource_id"),("observations","event_ns,source_key,source_row,oid"),
                         ("dependencies","did")):
        h.update(table.encode())
        for (body,) in db.execute(f"SELECT body FROM {table} ORDER BY {order}"):
            # Normalize enum/string JSON differences introduced by topology serialization.
            h.update(canonical_json(json.loads(body)).encode())
            h.update(b'\n')
    for row in db.execute("SELECT oid,state FROM trace_states ORDER BY oid"):
        h.update(canonical_json(list(row)).encode())
    return h.hexdigest()
