# DeepSeek Harness (DSH) Tool Mapping

Skills speak in actions ("create a todo", "dispatch a subagent", "read a file"). In DSH these resolve to the tools below. Load this file before running a skill that names tools from another harness.

| Action skills request | DSH equivalent |
|---|---|
| Create / update a todo list | `todo_write` (one todo per concrete step; keep it current) |
| Read, write, edit a file | `read`, `write`, `edit` (read before overwriting; prefer `edit`) |
| Search files or contents | `glob`, `grep` |
| Run a command | `pwsh` with `workdir`; use `run_in_background` plus `job_output` / `job_kill` for long work |
| Dispatch a subagent | `subagent` (fresh context, self-contained prompt) or `subagent_fork` (inherits this conversation) |
| Continue / steer / stop an agent | `send_message`, `list_agents`, `interrupt_agent` |
| Ask the user a question | `ask_user_question` (structured options); a live child agent cannot ask, so include the open question in its result |
| Load a skill | the `skill` tool with the exact name; a user may also invoke `/<name>` for user-invocable skills |
| Present a deliverable | `present` with the finished file paths |
| Search / fetch the web | `web_search`, `web_fetch` (no browser-automation tool) |
| Plan mode | explore read-only, then submit through `exit_plan_mode`; do not edit before approval |
| Long-running objective | `create_goal` / `get_goal` / `update_goal` |
| Large user-requested fan-out | `workflow` (only when the user explicitly asks for a workflow) |

## DSH-specific rules

- **Plan mode is binding.** Imperative requests are planned, not executed, until `exit_plan_mode` is approved. Exploration stays read-only.
- **Sandbox and approval.** A denied file operation or an automatically rejected approval request is a policy outcome: report the exact path/command, do not retry through another route, and do not claim success.
- **Subagents cannot ask the user.** `ask_user_question` from a runtime child fails with `DELEGATED_CALLER`; return the unresolved decision in the child's final result and let the parent ask.
- **Skill resources.** The `skill` result names a base directory for the skill (`<skill_resources>`); resolve relative resource paths against it. Prefer those paths over host-specific absolute paths.
- **Skill invocation split.** `disable-model-invocation: true` skills never appear in the catalog and are reachable only through `/<name>`; do not search for them with the `skill` tool.
- **MCP tools** are named `mcp__<serverName>__<toolName>`; do not guess names that are absent from the tool list.
- **Background jobs.** Keep every job id you start; collect still-relevant output with `job_output` before reporting, and `job_kill` jobs that no longer matter.
