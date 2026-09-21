# AxiomLite AI Routing

## Purpose

This file is the top-level routing layer for AI-assisted work on AxiomLite.

It determines which project context and skills should be activated for a task.

Do not load the entire `.ai/skills` directory for every task.

Use progressive disclosure.

## Initial Context

For non-trivial tasks, read:

.ai/PROJECT_CONTEXT.md

Then classify the task before loading deeper knowledge.

## General Routing Flow

Task
→ Understand
→ Classify
→ Identify Domain
→ Activate Relevant Skill
→ Inspect Repository
→ Implement Minimal Change
→ Verify
→ Review

## Repository-First Rule

The repository is the primary source of truth.

Before modifying code:

1. Inspect relevant files.
2. Inspect related models, services, views, templates, or configuration.
3. Search for existing implementations.
4. Reuse existing patterns when appropriate.

Do not rely on generic framework knowledge when repository evidence is available.

## Task Classification

Classify each task into one or more categories.

### Backend

Use the backend skill system when the task involves:

- Django
- Python backend code
- business logic
- services
- models
- views
- forms
- middleware
- background tasks
- backend architecture

Start with:

.ai/skills/backend/SKILL.md

Then follow the routing instructions defined by the backend skill.

### Django

For Django-specific tasks:

1. Start with the backend skill.
2. Follow its Django routing.
3. Load only the relevant Django-specific knowledge.

Inspect the actual Django application before changing code.

### API

For API-related tasks:

- Django REST Framework
- serializers
- API views
- viewsets
- permissions
- authentication
- filtering
- pagination
- schema generation

Start with the backend skill and activate the API-specific knowledge defined there.

### Database

For database-related tasks:

- Django ORM
- PostgreSQL
- migrations
- indexing
- query optimization
- transactions
- database architecture

Start with the backend skill and activate database-specific knowledge.

Never modify database structure without checking existing models and migrations.

### Security

For security-sensitive tasks:

- authentication
- authorization
- permissions
- sessions
- secrets
- file uploads
- subprocess execution
- Docker isolation
- untrusted input
- code execution

Start with the backend skill.

Then activate:

SECURITY_GUARDIAN.md

and any relevant domain-specific security knowledge.

Security-sensitive changes require explicit verification.

### Performance

For performance-related tasks:

- slow queries
- caching
- Redis
- Celery
- CPU usage
- memory usage
- response time
- code execution performance

Start with the backend skill.

Then activate:

PERFORMANCE_ENGINE.md

Only optimize after identifying the actual bottleneck when possible.

### Reliability

For reliability-related tasks:

- failures
- retries
- task execution
- error handling
- race conditions
- timeouts
- recovery
- external service failures

Start with the backend skill.

Then activate:

RELIABILITY_ENGINE.md

### Architecture

For architecture-level tasks:

- application boundaries
- service boundaries
- domain design
- major refactoring
- infrastructure decisions
- data flow
- system design

Start with:

.ai/skills/backend/SKILL.md

Then follow:

ARCHITECTURE_GENOME.md

DECISION_ENGINE.md

Use deeper domain knowledge only when necessary.

### Testing

For testing-related tasks:

- unit tests
- integration tests
- API tests
- security tests
- regression tests
- execution sandbox tests

Inspect the existing testing structure before creating new tests.

Prefer extending existing test patterns.

### Infrastructure

For infrastructure-related tasks:

- Docker
- Docker Compose
- deployment
- environment variables
- Redis
- PostgreSQL
- Celery
- Gunicorn
- Uvicorn

Inspect existing Dockerfiles, Compose files, scripts, and deployment configuration before making changes.

### Frontend

For frontend tasks:

- Django templates
- TailwindCSS
- DaisyUI
- JavaScript
- UI behavior

Preserve the server-rendered architecture.

Do not introduce React or another frontend framework unless explicitly requested.

## Cross-Domain Tasks

Some tasks activate multiple domains.

Examples:

### Secure Code Execution

Activate:

- backend
- security
- Docker/infrastructure
- performance
- reliability

### API Performance

Activate:

- backend
- API
- database
- performance

### Authentication

Activate:

- backend
- Django
- security
- API when applicable

### Celery Failure Handling

Activate:

- backend
- reliability
- infrastructure
- performance when relevant

## Progressive Disclosure

Use this order:

1. Relevant top-level project context
2. Relevant skill entry point
3. Relevant domain root
4. Specific domain knowledge
5. Specialized playbooks or incident knowledge

Do not read unrelated skill files.

## Reasoning Depth

Use deeper reasoning only when the task requires it.

Simple tasks should remain simple.

Do not activate the complete backend reasoning system for:

- trivial formatting
- simple renaming
- obvious documentation edits
- straightforward configuration changes

Complex architectural or security-sensitive tasks may require deeper reasoning.

## Verification

After implementation:

1. Check syntax.
2. Check imports.
3. Check affected configuration.
4. Run relevant tests when available.
5. Inspect the final diff.
6. Confirm that unrelated behavior was not changed.

Never claim that a command or test was executed unless it was actually executed.

## Change Scope

Prefer:

- minimal changes
- existing abstractions
- existing dependencies
- existing conventions

Avoid:

- unnecessary refactoring
- unrelated cleanup
- dependency proliferation
- large rewrites
- speculative architecture

## Final Response

For implementation tasks, report:

1. What changed
2. Which files changed
3. Verification performed
4. Any remaining uncertainty

Keep the final response concise unless more detail is requested.