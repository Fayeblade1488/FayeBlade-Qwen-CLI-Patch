# Coding agent usage
- Use small, iterative PRs.
- Never add secrets; prefer env vars & GitHub secrets.
- Respect CODEOWNERS; request reviews for protected paths.
- When unsure, prefer conservative defaults and create a draft PR with a checklist.

## Common prompts
- “Refactor module X to reduce cyclomatic complexity; keep public API stable.”
- “Add missing type hints, run mypy, fix warnings.”
- “Write tests for edge cases in Y; target >90% coverage for package Z.”
