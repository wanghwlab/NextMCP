# Software tests and workflow evaluation tasks

Maintainers and users validating an installation can run it with pytest.

```bash
# Synchronizes the Python environment
uv sync --extra dev

# Runs pytest in the project environment
uv run pytest
```

`conftest.py` provides shared temporary files, isolated test configuration, and helper
functions. 

## Test modules

| Module | What it checks |
| --- | --- |
| `test_cli.py` | CLI startup and options |
| `test_config.py` | Configuration loading and validation |
| `test_server.py` | HTTP/MCP assembly and authentication |
| `test_paths.py` | Read/write path restrictions |
| `test_fs_tools.py` | Filesystem tool behavior |
| `test_capability_tools.py` | Server information and readiness |
| `test_nextflow_tools.py` | Workflow preparation, launch, and related tools |
| `test_runtime_state.py` | Shared runtime state and configuration replacement |
| `test_tool_response.py` | Structured success/error responses |
| `test_tool_metadata.py` | Client-visible tool descriptions and metadata |
| `test_pipeline_visibility.py` | Safe handling of path-like strings during material redaction |
| `test_repository_skills.py` | Maintained package structure, runtime rules, and schema coverage |
| `test_expert_capability_scope.py` | Reasons for explicitly unsupported capabilities |
| `test_pipeline_expert_skill_creator_generator.py` | Skill generation, validation, and offline-evaluation helpers |
| `test_pipeline_support_contracts.py` | Task/specification structure, visibility rules, and documented launch conventions |


## Two different kinds of evaluation input

| Location | Evaluated behavior | Main contents |
| --- | --- | --- |
| `pipeline_support/<pipeline>/` | Translate a task into a specified run, complete it, and produce required outputs | Visible task, hidden specification, localization plan/script |
| `skills/experts/<pipeline>-expert-skill/evals/` | Use a skill to answer planning, parameter, output/QC, and coverage questions | Questions, expected answers, assertions |

Within `pipeline_support/`, `smoke.task.md` is visible to the evaluated agent; `smoke.yaml`
is the hidden evaluation specification. `smoke.localization.yaml` and `localize_testdata.py`
describe and prepare local inputs.

`test_pipeline_support_contracts.py` checks these reusable definitions.
