"""Research report generation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from atlas_backend.orchestration.models import ResearchSession, ResearchReport


class ReportGenerator:
    """Generates research reports from session evidence."""

    def generate_report(
        self,
        session: ResearchSession,
        title: str | None = None,
        executive_summary: str | None = None,
    ) -> ResearchReport:
        """Generate a report from a research session."""
        report = ResearchReport(
            session_id=session.session_id,
            title=title or session.title,
            executive_summary=executive_summary or f"Research report for {session.title}",
        )

        report.supporting_evidence = [e.evidence_id for e in session.evidence]

        for evidence in session.evidence:
            if evidence.source_url:
                report.citations.append({
                    "evidence_id": evidence.evidence_id,
                    "source": evidence.source_url,
                    "title": evidence.title,
                })

        return report

    def synthesize_sections(self, session: ResearchSession) -> list[dict[str, str]]:
        """Synthesize report sections from evidence."""
        sections = []

        search_results = [e for e in session.evidence if e.evidence_type == "search_result"]
        if search_results:
            section_content = "\n".join([f"- {e.title}: {e.content[:100]}..." for e in search_results[:5]])
            sections.append({
                "title": "Research Findings",
                "content": section_content,
            })

        analyses = [e for e in session.evidence if e.evidence_type == "analysis"]
        if analyses:
            section_content = "\n".join([f"- {e.title}: {e.content[:100]}..." for e in analyses[:5]])
            sections.append({
                "title": "Analysis",
                "content": section_content,
            })

        return sections

    def format_report_as_markdown(self, report: ResearchReport) -> str:
        """Format report as markdown."""
        markdown = f"# {report.title}\n\n"
        markdown += f"## Executive Summary\n{report.executive_summary}\n\n"

        if report.sections:
            for section in report.sections:
                markdown += f"## {section['title']}\n{section['content']}\n\n"

        if report.citations:
            markdown += "## Citations\n"
            for citation in report.citations:
                markdown += f"- [{citation['title']}]({citation['source']})\n"

        return markdown
