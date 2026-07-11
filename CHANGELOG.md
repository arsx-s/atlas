# Changelog

All notable Atlas changes are recorded here using semantic versioning.

## 0.7.2 - 2026-07-09

### Added

- Added a minimal Electron desktop shell with backend bootstrapping.
- Added a local dashboard for health checks and research session creation.
- Added beta-facing production, deployment, security, and provider setup documentation.

## 0.7.1 - 2026-07-09

### Fixed

- Restored backend test execution in the bundled Python runtime.
- Added graceful fallbacks for optional SQLAlchemy imports in persistence helpers.
- Fixed the missing `Optional` import in local runtime health checks.
- Fixed readiness status scoring for local runtime checks.
- Expanded the model registry to satisfy the expected provider coverage.
- Repaired projects package relative imports.
- Exported the document indexer interface from the package init.
- Replaced removed Pydantic v2 constrained types with supported validators.
- Added a robust RAM detection fallback when `psutil` is unavailable.

## 0.6.0 - 2026-07-09

### Added

- Established Milestone 6 document intelligence scope.
- Added document parsers for PDF, DOCX, Markdown, and TXT formats.
- Added OCR provider abstraction with Tesseract and cloud provider stubs.
- Added semantic and sliding-window document chunking strategies.
- Added document indexing interface and local vector index implementation.
- Added document ingestion pipeline orchestrating parse-chunk-embed-index workflow.
- Added document Q&A interface for querying document context with AI.
- Added document metadata, version tracking, and source highlighting models.
- Added document API routes (ingest, search, query, chunks).
- Added document unit tests (28 tests covering parsers, chunking, indexing, Q&A).
- Established Milestone 7 projects and knowledge scope.
- Added Project, Collection, Folder, Tag, Note, SavedResearch models.
- Added ProjectTimeline for activity tracking.
- Added project repository interfaces (ProjectRepository, CollectionRepository, NoteRepository, TagRepository, SavedResearchRepository, TimelineRepository).
- Added KnowledgeGraphInterface for Neo4j integration.
- Added ProjectManager orchestrating project operations.
- Added project API routes (create, get, list, notes, research, search, timeline).
- Added project unit tests (18 tests covering models, relationships, manager operations).
- Established Milestone 8 local intelligence scope.
- Added LocalModelRegistry with 6 models (Mistral, Llama, Gemma, Qwen, embeddings).
- Added HardwareDetector for CPU cores, RAM, and GPU detection.
- Added GPU configuration abstraction with NVIDIA, AMD, Apple support.
- Added OllamaLLMProvider interface for local model serving.
- Added LocalEmbeddingProvider interface for local embeddings.
- Added LocalVectorIndex for in-process semantic search.
- Added LocalCache for embedding and result caching.
- Added LocalMemoryProvider for conversation history and session memory.
- Added local runtime health checking with component status.
- Added local API routes (models, hardware, health, cache stats).
- Added local intelligence unit tests (36 tests covering models, hardware, caching, memory, health).
- Extended AtlasSettings with M6-M8 configuration (documents path, OCR provider, chunking strategy, knowledge graph, Ollama URL, local models).
- Extended health checks with M6-M8 component monitoring (documents storage, local runtime).

## 0.5.0 - 2026-07-09

### Added

- Established Milestone 4 AI provider abstraction scope.
- Added LLM provider interface with multi-provider support (OpenAI, Anthropic, Google, DeepSeek, local).
- Added embedding provider interface.
- Added search provider interface (Tavily, Brave Search, DuckDuckGo).
- Added model registry with 14+ supported models (GPT-4, Claude, Gemini, DeepSeek, Mistral, Llama, Gemma, Qwen, embeddings).
- Added provider routing and configuration.
- Added provider health checking interfaces.
- Added AI provider client stubs.
- Added AI provider unit tests (18 tests).
- Established Milestone 5 research pipeline orchestration scope.
- Added research session lifecycle management.
- Added task queue and task distribution.
- Added agent manager for multi-agent coordination.
- Added evidence and citation tracking with confidence scoring.
- Added research report generation with markdown formatting.
- Added research API routes (create session, get session, start, progress, report).
- Added research pipeline unit tests (19 tests).

## 0.4.0 - 2026-07-09

### Added

- Established Milestone 3 data layer scope.
- Added PostgreSQL session management with SQLAlchemy connection pooling.
- Added SQLite session management for local mode with foreign key support.
- Added repository interface abstractions for data access (UserRepository, ProjectRepository, DocumentRepository, LocalProfileRepository, LocalProjectRepository, SyncQueueRepository).
- Added provider interface abstractions for external services (QdrantProvider, Neo4jProvider, RedisProvider, StorageProvider).
- Added PostgreSQL Alembic migration baseline with cloud schema (users, devices, sessions, projects, research_sessions, documents, reports, sources, citations, settings, audit_logs).
- Added SQLite metadata schema for local mode (local_profiles, local_devices, local_projects, local_documents, sync_queue).
- Added datastore health check contracts for readiness reporting.
- Extended AtlasSettings with datastore configuration (DATABASE_URL, ATLAS_SQLITE_PATH, REDIS_URL, QDRANT_URL, NEO4J_URL, storage settings).
- Extended readiness reporting to include datastore component health checks.
- Added data layer unit tests (17 tests).

## 0.3.0 - 2026-07-08

### Added

- Established Milestone 1 foundation scope.
- Added project state, architecture, decisions, and implementation tracking files.
- Added monorepo workspace manifests for Desktop and Web.
- Added environment variable contract without committed secrets.
- Added foundation verification guard.
- Added foundation unit tests.
- Verified package manifests.
- Added Milestone 2 backend API core architecture artifact.
- Added typed backend configuration contract.
- Added standard Atlas API success and error response envelopes.
- Added Atlas exception and API error mapping.
- Added health and readiness contracts.
- Added local-device and cloud-user request principal boundaries.
- Added FastAPI app factory and v1 health route definitions.
- Added backend API core unit tests.

## 0.3.0 - 2026-07-09

### Added

- Established Milestone 4 AI provider abstraction scope.
- Added LLM provider interface with multi-provider support (OpenAI, Anthropic, Google, DeepSeek, local).
- Added embedding provider interface.
- Added search provider interface (Tavily, Brave Search, DuckDuckGo).
- Added model registry with 14+ supported models (GPT-4, Claude, Gemini, DeepSeek, Mistral, Llama, Gemma, Qwen).
- Added provider routing and configuration.
- Added provider health checking interfaces.
- Added AI provider client stubs.
- Added AI provider unit tests (18 tests).
- Established Milestone 5 research pipeline orchestration scope.
- Added research session lifecycle management.
- Added task queue and task distribution.
- Added agent manager for multi-agent coordination.
- Added evidence and citation tracking with confidence scoring.
- Added research report generation with markdown formatting.
- Added research API routes (create session, get session, start session, progress, report).
- Added research pipeline unit tests (19 tests).

## 0.2.0 - 2026-07-09

### Added

- Established Milestone 3 data layer scope.
- Added PostgreSQL session management with SQLAlchemy connection pooling.
- Added SQLite session management for local mode with foreign key support.
- Added repository interface abstractions for data access (UserRepository, ProjectRepository, DocumentRepository, LocalProfileRepository, LocalProjectRepository, SyncQueueRepository).
- Added provider interface abstractions for external services (QdrantProvider, Neo4jProvider, RedisProvider, StorageProvider).
- Added PostgreSQL Alembic migration baseline with cloud schema (users, devices, sessions, projects, research_sessions, documents, reports, sources, citations, settings, audit_logs).
- Added SQLite metadata schema for local mode (local_profiles, local_devices, local_projects, local_documents, sync_queue).
- Added datastore health check contracts for readiness reporting.
- Extended AtlasSettings with datastore configuration (DATABASE_URL, ATLAS_SQLITE_PATH, REDIS_URL, QDRANT_URL, NEO4J_URL, storage settings).
- Extended readiness reporting to include datastore component health checks.
- Added data layer unit tests (17 tests).

## 0.1.0 - 2026-07-08

### Added

- Established Milestone 1 foundation scope.
- Added project state, architecture, decisions, and implementation tracking files.
- Added monorepo workspace manifests for Desktop and Web.
- Added environment variable contract without committed secrets.
- Added foundation verification guard.
- Added foundation unit tests.
- Verified package manifests.
- Added Milestone 2 backend API core architecture artifact.
- Added typed backend configuration contract.
- Added standard Atlas API success and error response envelopes.
- Added Atlas exception and API error mapping.
- Added health and readiness contracts.
- Added local-device and cloud-user request principal boundaries.
- Added FastAPI app factory and v1 health route definitions.
- Added backend API core unit tests.
