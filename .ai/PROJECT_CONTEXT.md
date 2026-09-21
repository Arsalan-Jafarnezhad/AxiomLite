# OpenRouter Free Model Profile

## Identity

Model route:

```text
openrouter/free

Provider:

OpenRouter

This file describes project-level guidance for AI agents using the OpenRouter free model route.

It does not assume a specific underlying model.

The openrouter/free route may select different eligible models over time. Therefore, instructions must remain model-agnostic.

Role

The model is used as a general AI coding/reasoning model for work inside the AxiomLite repository.

Its primary project responsibilities are:

Understand existing code
Analyze repository structure
Follow project instructions
Route tasks through .ai/routing.md
Load relevant skills
Implement focused changes
Review existing implementations
Explain reasoning and trade-offs
Verify changes when possible
Required Project Context

Before performing a non-trivial repository task, consult:

.ai/PROJECT_CONTEXT.md
.ai/routing.md

For backend tasks, continue through:

.ai/skills/backend/SKILL.md

Do not read the entire .ai/skills/ tree.

Repository-First Behavior

When asked to modify AxiomLite:

Inspect the relevant source files.
Identify existing patterns.
Check related models, services, selectors, views, serializers, URLs, and tests.
Follow existing conventions.
Make the smallest reasonable change.
Verify the result.

Do not generate a new architecture when an existing project pattern already solves the problem.

Context Management

Because the underlying model selected by openrouter/free can vary:

Prefer concise relevant context.
Use progressive disclosure.
Avoid loading unrelated documentation.
Summarize large files mentally before continuing.
Load only the relevant skill/domain.
Do not repeat information already established by the project context.

When a task is simple, do not activate the full backend reasoning pipeline.

When a task is architectural, security-sensitive, or ambiguous, follow the relevant backend protocols more thoroughly.

Reasoning Guidance

Do not assume that every task requires maximum architectural complexity.

Prefer:

Existing solution
    ↓
Smallest correct change
    ↓
Measured improvement
    ↓
Larger architectural change only when justified

Consider:

Correctness
Security
Maintainability
Performance
Reliability
Complexity
Existing project conventions

The appropriate solution depends on the actual task.

Coding Guidance

When writing code:

Match existing style.
Preserve existing public behavior unless intentionally changing it.
Use existing abstractions where appropriate.
Avoid invented APIs.
Avoid speculative dependencies.
Avoid unrelated refactors.
Keep secrets out of code and output.
Treat external/user input as untrusted.
Treat submitted programming code as untrusted.

For Django:

Inspect existing models before changing schema.
Inspect migrations before modifying database structure.
Follow existing service/selector patterns.
Use transactions where the business operation requires atomicity.
Consider query count and N+1 behavior.
Respect existing permission boundaries.
Security

Security-sensitive tasks should activate:

.ai/skills/backend/SECURITY_GUARDIAN.md

Particular care is required for:

Authentication
Authorization
Payments
Secrets
File uploads
External requests
Webhooks
User-controlled URLs
Code execution
Docker sandboxing
Database access

Never claim that a system is absolutely secure.

State known limitations and uncertainties.

Verification

When possible, verify changes using the narrowest relevant checks.

Examples:

python configuration/manage.py check
pytest

or a targeted test:

pytest configuration/<app>/tests/

For frontend changes, use the project's existing npm scripts where relevant.

Do not claim that a test was run if it was not actually run.

Uncertainty

The underlying model for openrouter/free may change.

Therefore:

Do not assume a specific model identity.
Do not rely on undocumented model-specific behavior.
Do not assume a context-window size unless it is known from the active provider/model.
Do not claim tool availability without checking the current agent environment.

If a capability is unavailable, continue with the information available and clearly identify the limitation.

Tool Usage

MCP servers and external tools are separate from the model.

Do not assume that because this profile mentions OpenRouter, an OpenRouter MCP server is automatically available.

Use only tools actually exposed by the current agent environment.

Final Response

For implementation work, prefer this structure:

Summary
Files changed
Implementation
Verification
Notes / remaining uncertainty

Keep explanations proportional to the task.

Do not produce long architectural essays for simple fixes.