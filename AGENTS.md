# AxiomLite AI Instructions

## Project Context

Before non-trivial work, read:

.ai/PROJECT_CONTEXT.md

## Routing

Use:

.ai/routing.md

for task classification and skill routing.

## Skills

Reusable AI engineering knowledge is stored under:

.ai/skills/

For backend tasks, start with:

.ai/skills/backend/SKILL.md

Follow its progressive-disclosure system.

Do not load the entire skill tree unless necessary.

## General Rules

- Inspect existing code before changing it.
- Follow existing project conventions.
- Prefer minimal focused changes.
- Reuse existing abstractions.
- Do not invent APIs, models, settings, routes, or dependencies.
- Treat user-controlled input as untrusted.
- Treat submitted programming code as untrusted.
- Never expose secrets.
- Verify changes when possible.
- Do not claim tools or tests were used unless they were actually used.

## Source Priority

Use this priority when information conflicts:

1. Repository source code
2. Tests
3. Configuration
4. Project documentation
5. `.ai` context
6. General knowledge
7. Assumptions