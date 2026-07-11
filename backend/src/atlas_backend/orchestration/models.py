"""Research pipeline data models."""

from __future__ import annotations

from enum import StrEnum
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ResearchSessionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class EvidenceType(StrEnum):
    SEARCH_RESULT = "search_result"
    DOCUMENT_EXCERPT = "document_excerpt"
    MODEL_RESPONSE = "model_response"
    CITATION = "citation"
    ANALYSIS = "analysis"


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    agent_id: str
    task_type: str
    status: TaskStatus = TaskStatus.QUEUED
    description: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None


class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    evidence_type: EvidenceType
    title: str
    content: str
    source_url: str | None = None
    source_document: str | None = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    collected_by_task: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    user_id: str
    title: str
    description: str | None = None
    status: ResearchSessionStatus = ResearchSessionStatus.PENDING
    query: str
    model_used: str = "gpt-4"
    tasks: list[Task] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_cost: float = 0.0
    messages: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ResearchReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    title: str
    executive_summary: str
    sections: list[dict[str, str]] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    citations: list[dict[str, str]] = Field(default_factory=list)
    markdown_content: str = ""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
