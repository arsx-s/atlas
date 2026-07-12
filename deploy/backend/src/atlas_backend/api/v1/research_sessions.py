"""Research API routes with persistence and streaming."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.responses import create_success_response
from atlas_backend.orchestration.models import Evidence, EvidenceType, ResearchSession, ResearchSessionStatus, Task, TaskStatus, ResearchReport
from atlas_backend.orchestration.report_generator import ReportGenerator
from atlas_backend.orchestration.session import ResearchSessionManager
from atlas_backend.orchestration.evidence_tracker import EvidenceTracker
from atlas_backend.orchestration.task_queue import TaskQueue
from atlas_backend.orchestration.agent_manager import AgentManager
from atlas_backend.persistence import AtlasLocalStore
from atlas_backend.search.service import SearchService


_report_generator = ReportGenerator()


def _call_llm(prompt: str, model: str = "gpt-4", api_key: str = "") -> str:
    try:
        if "gpt" in model and api_key:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=2000
            )
            return resp.choices[0].message.content or ""
        elif "claude" in model:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
            return resp.content[0].text if resp.content else ""
        elif "gemini" in model:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            gen_model = genai.GenerativeModel(model)
            resp = gen_model.generate_content(prompt)
            return resp.text or ""
        else:
            return f"[Local mode simulation] Research analysis for: {prompt[:100]}..."
    except Exception as e:
        if not api_key:
            return f"[AI provider not configured. Set API keys to enable {model}.] Research analysis for query: {prompt[:200]}..."
        return f"[AI call failed: {e}] Simulated response for: {prompt[:100]}..."


def create_research_router(settings: Any, store: AtlasLocalStore) -> Any:
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import StreamingResponse

    router = APIRouter(tags=["research"])
    search_service = SearchService()

    @router.post("/chat")
    async def quick_chat(payload: dict[str, Any]) -> Any:
        """Auto-create project+session+chat in one call."""
        message = payload.get("message", "").strip()
        if not message:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Message is required.")
        user_id = payload.get("user_id", "local-user")
        model = payload.get("model", "gpt-4")
        api_key = payload.get("api_key", "")
        project_id = payload.get("project_id", "")
        if not project_id:
            projects = store.list_projects(user_id)
            if projects:
                project_id = projects[-1]["project_id"]
            else:
                project_id = str(uuid4())
                store.create_project({"project_id": project_id, "user_id": user_id, "name": "Research Project", "description": "Auto-created project for AI research", "tags": []})
                store.record_timeline_event({"event_id": str(uuid4()), "project_id": project_id, "event_type": "project_created", "description": "Project 'Research Project' created automatically"})
        session_id = payload.get("session_id", "")
        if not session_id:
            session_id = str(uuid4())
            title = message[:60] + ("..." if len(message) > 60 else "")
            store.create_research_session({"session_id": session_id, "project_id": project_id, "user_id": user_id, "title": title, "query": message, "description": "", "status": "active", "model_used": model, "messages": []})
            messages = []
        else:
            row = store.get_research_session(session_id)
            if not row:
                raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
            messages = row.get("messages", [])
        messages.append({"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()})
        response = _call_llm(message, model, api_key)
        messages.append({"role": "assistant", "content": response, "timestamp": datetime.now(timezone.utc).isoformat()})
        store.update_research_session(session_id, {"messages": messages})
        store.save_evidence({"evidence_id": str(uuid4()), "session_id": session_id, "evidence_type": "analysis", "title": message[:80], "content": response, "source_url": None, "source_document": None, "confidence_score": 1.0, "tags": [], "collected_by_task": None})
        return create_success_response({"project_id": project_id, "session_id": session_id, "response": response, "messages": messages})

    @router.post("/research-sessions")
    async def create_research_session(payload: dict[str, Any]) -> Any:
        project_id = payload.get("project_id", "")
        user_id = payload.get("user_id", "local-user")
        title = payload.get("title", "Research Session")
        query = payload.get("query", "")
        description = payload.get("description", "")
        model = payload.get("model", "gpt-4")

        if not project_id:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "project_id is required.")

        session = ResearchSession(
            project_id=project_id,
            user_id=user_id,
            title=title,
            query=query,
            description=description,
            model_used=model,
            messages=[],
        )
        store.create_research_session({
            "session_id": session.session_id,
            "project_id": session.project_id,
            "user_id": session.user_id,
            "title": session.title,
            "query": session.query,
            "description": session.description or "",
            "status": session.status.value,
            "model_used": session.model_used,
            "messages": [],
        })
        return create_success_response({
            "session_id": session.session_id,
            "status": session.status.value,
        })

    @router.get("/research-sessions/{session_id}")
    async def get_research_session(session_id: str) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        evidence = store.list_evidence(session_id)
        row["evidence"] = evidence
        return create_success_response(row)

    @router.get("/projects/{project_id}/research-sessions")
    async def list_research_sessions(project_id: str) -> Any:
        sessions = store.list_research_sessions(project_id)
        return create_success_response({"sessions": sessions})

    @router.post("/research-sessions/{session_id}/start")
    async def start_research_session(session_id: str) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        store.update_research_session(session_id, {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()})
        return create_success_response({"session_id": session_id, "status": "running"})

    @router.post("/research-sessions/{session_id}/chat")
    async def chat_research(session_id: str, payload: dict[str, Any]) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        message = payload.get("message", "").strip()
        if not message:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Message is required.")
        messages = row.get("messages", [])
        messages.append({"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()})
        api_key = payload.get("api_key", "")
        model = row.get("model_used", "gpt-4")
        response = _call_llm(message, model, api_key)
        messages.append({"role": "assistant", "content": response, "timestamp": datetime.now(timezone.utc).isoformat()})
        store.update_research_session(session_id, {"messages": messages})
        evidence = Evidence(session_id=session_id, evidence_type=EvidenceType.ANALYSIS, title=message[:80], content=response)
        store.save_evidence({
            "evidence_id": evidence.evidence_id,
            "session_id": evidence.session_id,
            "evidence_type": evidence.evidence_type.value,
            "title": evidence.title,
            "content": evidence.content,
            "source_url": None,
            "source_document": None,
            "confidence_score": evidence.confidence_score,
            "tags": evidence.tags,
            "collected_by_task": evidence.collected_by_task,
        })
        return create_success_response({"response": response, "messages": messages})

    @router.post("/research-sessions/{session_id}/chat/stream")
    async def chat_research_stream(session_id: str, payload: dict[str, Any]) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        message = payload.get("message", "").strip()
        if not message:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Message is required.")
        messages = row.get("messages", [])
        messages.append({"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()})
        api_key = payload.get("api_key", "")
        model = row.get("model_used", "gpt-4")

        async def event_stream():
            try:
                if "gpt" in model and api_key:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI(api_key=api_key)
                    stream = await client.chat.completions.create(
                        model=model, messages=[{"role": "user", "content": message}],
                        temperature=0.7, max_tokens=2000, stream=True
                    )
                    full = ""
                    async for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        if delta:
                            full += delta
                            yield f"data: {json.dumps({'type': 'chunk', 'content': delta})}\n\n"
                elif "claude" in model and api_key:
                    import anthropic
                    client = anthropic.AsyncAnthropic(api_key=api_key)
                    async with client.messages.stream(
                        model=model, max_tokens=2000, messages=[{"role": "user", "content": message}]
                    ) as stream:
                        full = ""
                        async for text in stream.text_stream:
                            full += text
                            yield f"data: {json.dumps({'type': 'chunk', 'content': text})}\n\n"
                elif api_key:
                    text = _call_llm(message, model, api_key)
                    yield f"data: {json.dumps({'type': 'chunk', 'content': text})}\n\n"
                else:
                    simulated = f"I'm analyzing your research question about '{message[:80]}'. Based on available information, I'd recommend starting with a literature review and formulating specific hypotheses. What aspect would you like to explore further?"
                    for word in simulated.split(" "):
                        yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
                        await asyncio.sleep(0.02)
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            finally:
                yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @router.post("/research-sessions/{session_id}/research")
    async def run_research(session_id: str, payload: dict[str, Any]) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        query = row.get("query", "")
        api_key = payload.get("api_key", "")
        model = row.get("model_used", "gpt-4")

        store.update_research_session(session_id, {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()})

        search_results = []
        try:
            results = await search_service.search(query, max_results=8)
            search_results = [r for r in results if not isinstance(r, Exception)]
        except Exception:
            pass

        for r in search_results[:5]:
            ev = Evidence(session_id=session_id, evidence_type=EvidenceType.SEARCH_RESULT,
                          title=r.title, content=r.snippet, source_url=r.url,
                          confidence_score=0.7, tags=["web_search"])
            store.save_evidence({
                "evidence_id": ev.evidence_id, "session_id": ev.session_id,
                "evidence_type": ev.evidence_type.value, "title": ev.title,
                "content": ev.content, "source_url": ev.source_url,
                "source_document": None, "confidence_score": ev.confidence_score,
                "tags": [], "collected_by_task": None,
            })

        search_context = "\n\n".join(
            f"Source: {r.title}\nURL: {r.url}\nContent: {r.snippet}" for r in search_results[:5]
        ) or "No search results available."

        analysis_prompt = f"""Research Query: {query}

Search Results:
{search_context}

Please provide a thorough research analysis covering:
1. Key findings from the search results
2. Critical analysis and evaluation
3. Gaps in the available information
4. Recommendations for further research
5. Citations for any sources used

Format your response with clear section headings."""

        analysis = _call_llm(analysis_prompt, model, api_key)
        ev = Evidence(session_id=session_id, evidence_type=EvidenceType.ANALYSIS,
                      title=f"Research Analysis: {query[:60]}", content=analysis,
                      confidence_score=0.8, tags=["analysis"])
        store.save_evidence({
            "evidence_id": ev.evidence_id, "session_id": ev.session_id,
            "evidence_type": ev.evidence_type.value, "title": ev.title,
            "content": ev.content, "source_url": None,
            "source_document": None, "confidence_score": ev.confidence_score,
            "tags": [], "collected_by_task": None,
        })

        store.update_research_session(session_id, {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()})
        return create_success_response({"status": "completed", "analysis": analysis, "search_results_count": len(search_results)})

    @router.get("/research-sessions/{session_id}/progress")
    async def get_research_progress(session_id: str) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        evidence = store.list_evidence(session_id)
        return create_success_response({
            "session_id": session_id,
            "status": row["status"],
            "evidence_count": len(evidence),
            "message_count": len(row.get("messages", [])),
        })

    @router.post("/research-sessions/{session_id}/generate-report")
    async def generate_report(session_id: str) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        evidence = store.list_evidence(session_id)

        sections = []
        citations = []
        for e in evidence:
            if e["evidence_type"] == "search_result":
                sections.append({"heading": "Search Results", "content": f"**{e['title']}**: {e['content']}"})
                if e.get("source_url"):
                    citations.append({"text": e["title"], "source": e["source_url"]})

        for e in evidence:
            if e["evidence_type"] == "analysis":
                sections.append({"heading": "Analysis", "content": e["content"]})

        report = ResearchReport(
            session_id=session_id,
            title=row["title"],
            executive_summary=evidence[0]["content"][:500] if evidence else "No evidence collected.",
            sections=sections,
            citations=citations,
        )

        markdown_lines = [f"# {report.title}", "", "## Executive Summary", report.executive_summary, ""]
        for s in sections:
            markdown_lines.append(f"## {s['heading']}")
            markdown_lines.append(s["content"])
            markdown_lines.append("")
        if citations:
            markdown_lines.append("## Citations")
            for i, c in enumerate(citations, 1):
                markdown_lines.append(f"[{i}] {c['text']} — {c['source']}")
        report.markdown_content = "\n".join(markdown_lines)

        store.save_report({
            "report_id": report.report_id,
            "session_id": report.session_id,
            "title": report.title,
            "executive_summary": report.executive_summary,
            "sections": report.sections,
            "supporting_evidence": report.supporting_evidence,
            "citations": report.citations,
            "markdown_content": report.markdown_content,
        })
        return create_success_response(report.model_dump(mode="json"))

    @router.get("/research-sessions/{session_id}/report")
    async def get_research_report(session_id: str) -> Any:
        report = store.get_report(session_id)
        if not report:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, "No report generated yet for this session.")
        return create_success_response(report)

    @router.post("/research-sessions/{session_id}/evidence")
    async def add_research_evidence(session_id: str, payload: dict[str, Any]) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        evidence = Evidence(
            session_id=session_id,
            evidence_type=EvidenceType(payload.get("evidence_type", EvidenceType.ANALYSIS)),
            title=payload.get("title", "Evidence"),
            content=payload.get("content", ""),
            source_url=payload.get("source_url"),
            source_document=payload.get("source_document"),
            confidence_score=float(payload.get("confidence_score", 1.0)),
            tags=list(payload.get("tags") or []),
            collected_by_task=payload.get("collected_by_task"),
        )
        store.save_evidence({
            "evidence_id": evidence.evidence_id, "session_id": evidence.session_id,
            "evidence_type": evidence.evidence_type.value, "title": evidence.title,
            "content": evidence.content, "source_url": evidence.source_url,
            "source_document": evidence.source_document,
            "confidence_score": evidence.confidence_score,
            "tags": evidence.tags, "collected_by_task": evidence.collected_by_task,
        })
        return create_success_response(evidence.model_dump(mode="json"))

    @router.get("/research-sessions/{session_id}/evidence")
    async def list_research_evidence(session_id: str) -> Any:
        evidence = store.list_evidence(session_id)
        return create_success_response({"evidence": evidence})

    @router.delete("/research-sessions/{session_id}")
    async def delete_research_session(session_id: str) -> Any:
        row = store.get_research_session(session_id)
        if not row:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, f"Research session '{session_id}' not found.")
        store.update_research_session(session_id, {"status": "cancelled"})
        return create_success_response({"deleted": True})

    return router
