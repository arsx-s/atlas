"""Knowledge graph interfaces."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GraphNode(BaseModel):
    """A node in the knowledge graph."""
    node_id: str
    node_type: str  # person, organization, concept, claim, document
    label: str
    properties: dict = {}


class GraphEdge(BaseModel):
    """An edge connecting nodes."""
    edge_id: str
    source_id: str
    target_id: str
    relationship: str  # related_to, cites, authored_by, etc.
    weight: float = 1.0
    properties: dict = {}


class KnowledgeGraphInterface(ABC):
    """Knowledge graph abstraction for Neo4j."""

    @abstractmethod
    async def add_node(self, node: GraphNode, project_id: UUID) -> str:
        """Add a node to the graph."""
        pass

    @abstractmethod
    async def add_edge(self, edge: GraphEdge, project_id: UUID) -> str:
        """Add an edge to the graph."""
        pass

    @abstractmethod
    async def query_related(
        self, node_id: str, project_id: UUID, depth: int = 2
    ) -> dict:
        """Find related nodes (up to specified depth)."""
        pass

    @abstractmethod
    async def search_nodes(self, query: str, project_id: UUID, limit: int = 20) -> list[GraphNode]:
        """Search nodes by label or properties."""
        pass

    @abstractmethod
    async def get_graph_summary(self, project_id: UUID) -> dict:
        """Get graph statistics (node/edge counts, density, etc.)."""
        pass
