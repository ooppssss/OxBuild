from pydantic import BaseModel
from typing import Optional

class TextIngestRequest(BaseModel):
    text: str
    doc_id: Optional[str] = None



class Node(BaseModel):
    id: str
    label: str
    doc_ids: list[str] = []

class Edge(BaseModel):
    source: str
    target: str
    relation: str
    source_text: str
    doc_id: str


class GraphData(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class IngestResponse(BaseModel):
    doc_id: str
    chunks_processed: int
    triplets_extracted: int
    nodes_added: int
    edges_added: int
    graph: GraphData

class QueryResponse(BaseModel):
    entity: str
    depth: str
    subgraph: GraphData


class InferenceResult(BaseModel):
    from_entity: str
    to_entity: str
    suggested_relation: str
    reasoning: str
    confidence: str

class InferenceResponse(BaseModel):
    insights: list[InferenceResult]

class RawTriplet(BaseModel):
    source: str
    relation: str
    target: str
    source_text: str
    doc_id: str
 