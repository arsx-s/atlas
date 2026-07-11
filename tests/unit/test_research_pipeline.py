"""Unit tests for research pipeline (Milestone 5)."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.orchestration.models import (
    ResearchSessionStatus,
    TaskStatus,
    EvidenceType,
    Task,
    Evidence,
    ResearchSession,
    ResearchReport,
)
from atlas_backend.orchestration.session import ResearchSessionManager
from atlas_backend.orchestration.task_queue import TaskQueue
from atlas_backend.orchestration.agent_manager import AgentManager
from atlas_backend.orchestration.evidence_tracker import EvidenceTracker
from atlas_backend.orchestration.report_generator import ReportGenerator


class ResearchPipelineTests(unittest.TestCase):
    """Test research pipeline orchestration."""

    def test_research_session_creation(self) -> None:
        """Verify research session can be created."""
        manager = ResearchSessionManager()
        session = manager.create_session(
            project_id="proj-1",
            user_id="user-1",
            title="Test Research",
            query="What is machine learning?",
        )
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.title, "Test Research")
        self.assertEqual(session.status, ResearchSessionStatus.PENDING)

    def test_research_session_status_transitions(self) -> None:
        """Verify research session status transitions."""
        manager = ResearchSessionManager()
        session = manager.create_session(
            project_id="proj-1",
            user_id="user-1",
            title="Test",
            query="Test query",
        )
        manager.update_session_status(session.session_id, ResearchSessionStatus.RUNNING)
        updated = manager.get_session(session.session_id)
        self.assertEqual(updated.status, ResearchSessionStatus.RUNNING)
        self.assertIsNotNone(updated.started_at)

    def test_task_queue_enqueue_dequeue(self) -> None:
        """Verify task queue operations."""
        queue = TaskQueue()
        task = Task(
            session_id="sess-1",
            agent_id="agent-1",
            task_type="search",
            description="Search for information",
        )
        queue.enqueue_task("sess-1", task)
        self.assertEqual(queue.get_queue_length("sess-1"), 1)

        dequeued = queue.dequeue_task("sess-1")
        self.assertIsNotNone(dequeued)
        self.assertEqual(dequeued.task_id, task.task_id)
        self.assertEqual(queue.get_queue_length("sess-1"), 0)

    def test_task_assignment(self) -> None:
        """Verify task assignment to agents."""
        queue = TaskQueue()
        task = Task(
            session_id="sess-1",
            agent_id="agent-1",
            task_type="search",
            description="Test",
        )
        queue.enqueue_task("sess-1", task)
        queue.assign_task(task.task_id, "agent-1")
        assigned = queue.get_assigned_task(task.task_id)
        self.assertIsNotNone(assigned)
        self.assertEqual(assigned.status, TaskStatus.ASSIGNED)

    def test_agent_manager_registration(self) -> None:
        """Verify agent registration."""
        manager = AgentManager()
        mock_agent = {"name": "test_agent"}
        manager.register_agent("agent-1", mock_agent)
        retrieved = manager.get_agent("agent-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "test_agent")

    def test_agent_availability_tracking(self) -> None:
        """Verify agent availability tracking."""
        manager = AgentManager()
        manager.register_agent("agent-1", {})
        manager.register_agent("agent-2", {})

        available = manager.get_available_agents()
        self.assertEqual(len(available), 2)

        manager.mark_agent_busy("agent-1")
        available = manager.get_available_agents()
        self.assertEqual(len(available), 1)
        self.assertIn("agent-2", available)

        manager.mark_agent_idle("agent-1")
        available = manager.get_available_agents()
        self.assertEqual(len(available), 2)

    def test_evidence_tracking(self) -> None:
        """Verify evidence tracking."""
        tracker = EvidenceTracker()
        evidence = Evidence(
            session_id="sess-1",
            evidence_type=EvidenceType.SEARCH_RESULT,
            title="Test Result",
            content="Test content",
            source_url="http://example.com",
        )
        tracker.add_evidence("sess-1", evidence)
        retrieved = tracker.get_evidence("sess-1")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].title, "Test Result")

    def test_evidence_filtering_by_type(self) -> None:
        """Verify evidence filtering by type."""
        tracker = EvidenceTracker()
        search_evidence = Evidence(
            session_id="sess-1",
            evidence_type=EvidenceType.SEARCH_RESULT,
            title="Search",
            content="Search content",
        )
        analysis_evidence = Evidence(
            session_id="sess-1",
            evidence_type=EvidenceType.ANALYSIS,
            title="Analysis",
            content="Analysis content",
        )
        tracker.add_evidence("sess-1", search_evidence)
        tracker.add_evidence("sess-1", analysis_evidence)

        search_only = tracker.get_evidence_by_type("sess-1", EvidenceType.SEARCH_RESULT)
        self.assertEqual(len(search_only), 1)
        self.assertEqual(search_only[0].evidence_type, EvidenceType.SEARCH_RESULT)

    def test_citation_tracking(self) -> None:
        """Verify citation tracking."""
        tracker = EvidenceTracker()
        citation = {
            "id": "cite-1",
            "source": "http://example.com",
            "title": "Test Citation",
        }
        tracker.add_citation("sess-1", citation)
        citations = tracker.get_citations("sess-1")
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["title"], "Test Citation")

    def test_report_generation(self) -> None:
        """Verify report generation from session."""
        session = ResearchSession(
            project_id="proj-1",
            user_id="user-1",
            title="Test Research",
            query="Test query",
        )
        evidence = Evidence(
            session_id=session.session_id,
            evidence_type=EvidenceType.SEARCH_RESULT,
            title="Result",
            content="Content",
        )
        session.evidence.append(evidence)

        generator = ReportGenerator()
        report = generator.generate_report(session)
        self.assertIsNotNone(report.report_id)
        self.assertEqual(report.session_id, session.session_id)
        self.assertEqual(len(report.supporting_evidence), 1)

    def test_report_markdown_formatting(self) -> None:
        """Verify report markdown formatting."""
        report = ResearchReport(
            session_id="sess-1",
            title="Test Report",
            executive_summary="This is a test",
        )
        report.sections.append({
            "title": "Test Section",
            "content": "Test content",
        })

        generator = ReportGenerator()
        markdown = generator.format_report_as_markdown(report)
        self.assertIn("# Test Report", markdown)
        self.assertIn("## Executive Summary", markdown)
        self.assertIn("## Test Section", markdown)

    def test_high_confidence_evidence_filtering(self) -> None:
        """Verify high confidence evidence filtering."""
        tracker = EvidenceTracker()
        high_conf = Evidence(
            session_id="sess-1",
            evidence_type=EvidenceType.SEARCH_RESULT,
            title="High",
            content="Content",
            confidence_score=0.95,
        )
        low_conf = Evidence(
            session_id="sess-1",
            evidence_type=EvidenceType.SEARCH_RESULT,
            title="Low",
            content="Content",
            confidence_score=0.6,
        )
        tracker.add_evidence("sess-1", high_conf)
        tracker.add_evidence("sess-1", low_conf)

        high_only = tracker.get_high_confidence_evidence("sess-1", threshold=0.8)
        self.assertEqual(len(high_only), 1)
        self.assertEqual(high_only[0].title, "High")

    def test_session_progress_tracking(self) -> None:
        """Verify session progress tracking."""
        manager = ResearchSessionManager()
        session = manager.create_session(
            project_id="proj-1",
            user_id="user-1",
            title="Test",
            query="Test",
        )
        progress = manager.get_session_progress(session.session_id)
        self.assertEqual(progress["total_tasks"], 0)
        self.assertEqual(progress["completed_tasks"], 0)

    def test_evidence_summary(self) -> None:
        """Verify evidence summary generation."""
        tracker = EvidenceTracker()
        for i in range(3):
            evidence = Evidence(
                session_id="sess-1",
                evidence_type=EvidenceType.SEARCH_RESULT,
                title=f"Result {i}",
                content="Content",
                confidence_score=0.9,
            )
            tracker.add_evidence("sess-1", evidence)

        summary = tracker.get_evidence_summary("sess-1")
        self.assertEqual(summary["total_evidence"], 3)
        self.assertEqual(summary["high_confidence_evidence"], 3)


if __name__ == "__main__":
    unittest.main()
