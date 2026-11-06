"""Typed observed graph plus an explicitly separate evaluation-label graph."""
from dataclasses import asdict
import networkx as nx
from .domain import RELATION_CATEGORY, TraceSpan, digest


def edge(graph, source, target, relation, key, **attrs):
    if source not in graph or target not in graph:
        raise ValueError("edge endpoints must exist")
    if relation not in RELATION_CATEGORY:
        raise ValueError("unsupported relation")
    graph.add_edge(source,target,key=key,relation=relation,
                   category=RELATION_CATEGORY[relation],**attrs)


def build_graph(incident):
    graph = nx.MultiDiGraph(scope="operational",schema_version="dce-graph-v1")
    graph.add_node(incident.id,kind="incident",environment=incident.environment,
                   start_ns=incident.start_ns,end_ns=incident.end_ns)
    for entity in sorted(incident.entities.values(),key=lambda e:e.id):
        graph.add_node(entity.id,**asdict(entity),node_type="entity")
    span_lookup = {(o.trace_id,o.span_id): [] for o in incident.observations if isinstance(o,TraceSpan)}
    for o in incident.observations:
        graph.add_node(o.id,**asdict(o),node_type="observation")
        edge(graph,incident.id,o.id,"HAS_OBSERVATION",o.id)
        edge(graph,o.id,o.entity_id,"OBSERVED_ON",o.id)
        if isinstance(o,TraceSpan):
            trace_node="trace:"+digest([incident.environment,o.trace_id])
            graph.add_node(trace_node,kind="trace",source_id=o.trace_id)
            edge(graph,o.id,trace_node,"IN_TRACE",o.id)
            span_lookup[(o.trace_id,o.span_id)].append(o)
    for d in incident.dependencies:
        edge(graph,d.source_entity,d.target_entity,d.relation,d.id,
             evidence_ids=list(d.evidence_ids),time=asdict(d.time))
        evidence="evidence:"+d.id
        graph.add_node(evidence,kind="dependency_evidence",dependency_id=d.id)
        for oid in d.evidence_ids:
            edge(graph,evidence,oid,"SUPPORTED_BY",oid)
    for o in incident.observations:
        if isinstance(o,TraceSpan) and o.parent_span_id:
            parents=span_lookup.get((o.trace_id,o.parent_span_id),[])
            if len(parents)==1 and parents[0].id!=o.id:
                edge(graph,parents[0].id,o.id,"PARENT_SPAN",o.id)
    return graph


def build_evaluation_graph(incident):
    graph=nx.MultiDiGraph(scope="evaluation_only",schema_version="dce-graph-v1")
    graph.add_node(incident.id,kind="incident")
    for f in incident.ground_truth.events:
        graph.add_node(f.id,kind="labelled_fault",**asdict(f))
        graph.add_node(f.entity_id,kind="label_reference",observed=f.entity_id in incident.entities)
        edge(graph,incident.id,f.id,"CONTAINS",f.id)
        edge(graph,f.id,f.entity_id,"AFFECTS",f.id)
    return graph


def graph_dict(graph):
    return {"metadata": dict(graph.graph),
            "nodes": [{"id": n,"attributes": attrs} for n,attrs in sorted(graph.nodes(data=True))],
            "edges": [{"source":s,"target":t,"key":k,"attributes":a}
                      for s,t,k,a in sorted(graph.edges(keys=True,data=True),key=lambda x:x[:3])]}
