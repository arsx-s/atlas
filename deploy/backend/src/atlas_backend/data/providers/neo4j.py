"""Local graph database provider."""

from __future__ import annotations

import itertools
from typing import Any

from atlas_backend.data.providers import Neo4jProvider


class Neo4jProviderImpl(Neo4jProvider):
    """Concrete Neo4j provider implementation backed by in-memory graph state."""

    def __init__(self) -> None:
        self._node_counter = itertools.count(1)
        self._nodes: dict[str, dict[str, Any]] = {}
        self._relationships: list[dict[str, Any]] = []

    def execute_query(self, query: str, parameters: dict | None = None) -> list:
        query_text = query.strip().lower()
        if query_text.startswith("match") and "return" in query_text:
            if "relationship" in query_text or "-[" in query_text:
                return list(self._relationships)
            return list(self._nodes.values())
        return [{"query": query, "parameters": parameters or {}, "nodes": len(self._nodes), "relationships": len(self._relationships)}]

    def create_node(self, label: str, properties: dict) -> dict:
        node_id = str(next(self._node_counter))
        node = {"id": node_id, "label": label, "properties": dict(properties)}
        self._nodes[node_id] = node
        return node

    def create_relationship(self, from_node_id: str, to_node_id: str, relationship_type: str, properties: dict | None = None) -> bool:
        if from_node_id not in self._nodes or to_node_id not in self._nodes:
            return False
        self._relationships.append(
            {
                "from": from_node_id,
                "to": to_node_id,
                "type": relationship_type,
                "properties": dict(properties or {}),
            },
        )
        return True

    def delete_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        self._nodes.pop(node_id, None)
        self._relationships = [relationship for relationship in self._relationships if relationship["from"] != node_id and relationship["to"] != node_id]
        return True
