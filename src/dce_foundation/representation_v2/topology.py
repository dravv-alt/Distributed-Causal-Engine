"""Workbook cell evidence and trace reference resolution, without causal claims."""
from collections import Counter
from dataclasses import asdict
import io
import re
import xml.etree.ElementTree as ET
import zipfile
import networkx as nx
from ..domain import digest
from .model import SourceRef, ResourceKind, resource, Dependency, Relation

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
TYPE_KINDS = {"oracle_11G": ResourceKind.DATABASE, "redis": ResourceKind.CACHE,
              "docker": ResourceKind.CONTAINER, "OS": ResourceKind.HOST}


def workbook_topology(payload, source_key):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(e.itertext()) for e in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        cells = {}
        rows = sheet.findall(".//s:row", NS)
        for row in rows:
            for c in row.findall("s:c", NS):
                raw = c.findtext("s:v", default="", namespaces=NS)
                cells[c.get("r")] = strings[int(raw)] if c.get("t") == "s" else (
                    "".join(c.find("s:is", NS).itertext()) if c.get("t") == "inlineStr" else raw)
        origins = {k:k for k in cells}
        for merge in sheet.findall(".//s:mergeCell", NS):
            first, last = merge.get("ref").split(":")
            a = re.fullmatch(r"([A-Z]+)(\d+)", first)
            b = re.fullmatch(r"([A-Z]+)(\d+)", last)
            # Only same-column merges are safe to propagate. A63:D63 is a heading.
            if a[1] == b[1]:
                for n in range(int(a[2]), int(b[2]) + 1):
                    target = a[1] + str(n)
                    cells[target] = cells.get(first, "")
                    origins[target] = first
        if [cells.get(x + "1") for x in "ABCDE"] != ["Type","Number","Host","Name","From (containers)"]:
            raise ValueError("unexpected deployment workbook header")
        resources, deps, aliases = {}, [], []
        for r in rows:
            n = int(r.get("r"))
            if n == 1:
                continue
            values = {col:cells.get(col + str(n), "") for col in "ABCDE"}
            name, host, kind = values["D"], values["C"], values["A"]
            if not name:
                continue
            ref = SourceRef("OpenRCA-deployment-workbook", source_key, n, values,
                            {"cell_origins": {c:origins.get(c + str(n)) for c in "ABCDE"}})
            entity = resource("Telecom", name, ref, TYPE_KINDS.get(kind, ResourceKind.UNKNOWN))
            previous = resources.get(entity.resource_id)
            if previous is None or previous.resource_kind == ResourceKind.UNKNOWN:
                resources[entity.resource_id] = entity
            elif entity.resource_kind not in (ResourceKind.UNKNOWN, previous.resource_kind):
                raise ValueError("conflicting workbook resource kinds")
            if host:
                target = resource("Telecom", host, ref, ResourceKind.HOST)
                resources[target.resource_id] = target
                deps.append(Dependency("dependency:" + digest([source_key,n,"RUNS_ON"]),
                    entity.resource_id, target.resource_id, Relation.RUNS_ON,
                    (source_key + ":C" + str(n), source_key + ":D" + str(n)), ref))
            if values["E"]:
                aliases.append({"source_name": name, "candidate": values["E"],
                                "meaning": "From (containers); deployment hint, not identity equivalence",
                                "status": "unreviewed_not_applied", "provenance": asdict(ref)})
        return resources, deps, {"xml_rows":len(rows), "named_resources":len(resources),
                                  "runs_on":len(deps), "alias_candidates":aliases}


def resolve_trace_context(db):
    """Resolve against the bounded stored context. Full scan uses the same disk index."""
    db.execute("CREATE INDEX IF NOT EXISTS span_identity ON spans(environment,trace_id,span_id)")
    counts = Counter()
    for oid, env, trace, span, parent, rid, ns, key, row in db.execute(
            "SELECT oid,environment,trace_id,span_id,parent_id,resource_id,event_ns,source_key,source_row FROM spans ORDER BY oid"):
        if parent is None:
            state = "missing_parent_or_root_unknown"
            matches = []
        elif parent == span:
            state = "self_parent_convention_unknown"
            matches = []
        else:
            matches = db.execute("SELECT oid,resource_id FROM spans WHERE environment=? AND trace_id=? AND span_id=? LIMIT 2",
                                 (env, trace, parent)).fetchall()
            state = "unresolved_parent" if not matches else ("ambiguous_parent" if len(matches) != 1 else "resolved_parent")
        counts[state] += 1
        db.execute("INSERT INTO trace_states VALUES (?,?)", (oid,state))
        if state == "resolved_parent":
            p = matches[0]
            dep = Dependency("dependency:" + digest([p[0],oid]), p[1], rid, Relation.CALLS,
                             (p[0],oid), SourceRef("OpenRCA",key,row,{}, {"parent_resolution":state}), event_ns=ns)
            db.execute("INSERT INTO dependencies VALUES (?, ?, ?, ?)",
                       (dep.dependency_id, dep.event_ns, dep.relation_type.value, __import__('json').dumps(asdict(dep),sort_keys=True)))
    return dict(counts)


def typed_graph(resources, dependencies):
    graph = nx.MultiDiGraph(schema_version="dce-v2", epistemic_status="OBSERVED")
    for r in resources:
        graph.add_node(r.resource_id, node_type="Resource", resource_kind=r.resource_kind.value)
    for d in dependencies:
        if d.epistemic_status != "OBSERVED" or d.source not in graph or d.target not in graph or not d.evidence:
            raise ValueError("unsupported relation or missing evidence/resource")
        graph.add_edge(d.source,d.target,key=d.dependency_id,relation_type=d.relation_type.value,
                       epistemic_status=d.epistemic_status,evidence=d.evidence)
    return graph
