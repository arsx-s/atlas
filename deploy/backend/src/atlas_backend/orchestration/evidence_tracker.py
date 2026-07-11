"""Evidence and citation tracking."""

from __future__ import annotations

from typing import Any

from atlas_backend.orchestration.models import Evidence, EvidenceType


class EvidenceTracker:
    """Tracks evidence and citations."""

    def __init__(self) -> None:
        self._evidence: dict[str, list[Evidence]] = {}
        self._citations: dict[str, list[dict[str, Any]]] = {}

    def add_evidence(self, session_id: str, evidence: Evidence) -> None:
        """Record evidence for a session."""
        if session_id not in self._evidence:
            self._evidence[session_id] = []
        self._evidence[session_id].append(evidence)

    def get_evidence(self, session_id: str) -> list[Evidence]:
        """Get all evidence for a session."""
        return self._evidence.get(session_id, [])

    def get_evidence_by_type(self, session_id: str, evidence_type: EvidenceType) -> list[Evidence]:
        """Get evidence filtered by type."""
        evidence_list = self._evidence.get(session_id, [])
        return [e for e in evidence_list if e.evidence_type == evidence_type]

    def add_citation(self, session_id: str, citation: dict[str, Any]) -> None:
        """Record a citation."""
        if session_id not in self._citations:
            self._citations[session_id] = []
        self._citations[session_id].append(citation)

    def get_citations(self, session_id: str) -> list[dict[str, Any]]:
        """Get all citations for a session."""
        return self._citations.get(session_id, [])

    def link_evidence_to_citation(self, session_id: str, evidence_id: str, citation_id: str) -> bool:
        """Link evidence to a citation."""
        evidence_list = self._evidence.get(session_id, [])
        for evidence in evidence_list:
            if evidence.evidence_id == evidence_id:
                evidence.tags.append(f"citation:{citation_id}")
                return True
        return False

    def get_high_confidence_evidence(self, session_id: str, threshold: float = 0.8) -> list[Evidence]:
        """Get evidence above confidence threshold."""
        evidence_list = self._evidence.get(session_id, [])
        return [e for e in evidence_list if e.confidence_score >= threshold]

    def get_evidence_summary(self, session_id: str) -> dict[str, Any]:
        """Get summary of evidence collected."""
        evidence_list = self._evidence.get(session_id, [])
        citations_list = self._citations.get(session_id, [])

        return {
            "total_evidence": len(evidence_list),
            "high_confidence_evidence": len([e for e in evidence_list if e.confidence_score >= 0.8]),
            "total_citations": len(citations_list),
            "evidence_by_type": {
                ev_type.value: len([e for e in evidence_list if e.evidence_type == ev_type])
                for ev_type in EvidenceType
            },
        }
