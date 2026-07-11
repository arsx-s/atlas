"""Local vector database provider."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from atlas_backend.data.providers import QdrantProvider


class QdrantProviderImpl(QdrantProvider):
    """Concrete Qdrant provider implementation backed by in-memory collections."""

    def __init__(self) -> None:
        self._collections: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
        self._vector_sizes: dict[str, int] = {}

    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        self._collections.setdefault(collection_name, {})
        self._vector_sizes[collection_name] = vector_size
        return True

    def upsert_vectors(self, collection_name: str, points: list[dict[str, Any]]) -> bool:
        if collection_name not in self._collections:
            self.create_collection(collection_name, len(points[0].get("vector", [])) if points else 0)
        for point in points:
            point_id = int(point["id"])
            self._collections[collection_name][point_id] = point
        return True

    def search_vectors(self, collection_name: str, query_vector: list[float], limit: int = 10) -> list[dict[str, Any]]:
        collection = self._collections.get(collection_name, {})
        scored: list[dict[str, Any]] = []
        for point_id, point in collection.items():
            vector = [float(value) for value in point.get("vector", [])]
            score = self._cosine_similarity(query_vector, vector)
            scored.append({"id": point_id, "score": score, **point})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:limit]

    def delete_vectors(self, collection_name: str, point_ids: list[int]) -> bool:
        collection = self._collections.get(collection_name)
        if collection is None:
            return False
        for point_id in point_ids:
            collection.pop(int(point_id), None)
        return True

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[index] * right[index] for index in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size]))
        right_norm = math.sqrt(sum(value * value for value in right[:size]))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)
