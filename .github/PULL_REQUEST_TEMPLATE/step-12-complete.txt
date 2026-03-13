---
title: Step 12: MCPAgent (MCP subagent)
labels: enhancement, agent, mcp, step-12
---

## What does this PR do?

Implements the MCPAgent subagent for proxying tool calls to external MCP servers via HTTP. This completes Step 12 of the agent build plan.

- Discovers tools from all configured MCP servers at startup via `GET {server_url}/tools`.
- Wraps each discovered tool as a LangChain StructuredTool, qualifying names to avoid collisions.
- Forwards tool invocations via `POST {server_url}/tools/{tool_name}`.
- Handles no-server and unreachable-server cases gracefully, returning a notice instead of error.
- Follows the same LLM-ToolNode loop as ToolUseAgent.
- Full unit test coverage for all helper functions and graph paths.
- Documentation updated in `docs/modules/agents.md`.

## How was this validated?

- All tests pass (pytest, 74 passed, 14 skipped).
- Ruff and mypy: no issues found.
- Manual review of code, tests, and docs for completeness and clarity.

## Checklist

- [x] Code, tests, and docs present and validated
- [x] All tests pass
- [x] Lint and type checks pass
- [x] Documentation updated

Ready for review and merge.
