# Software tests and workflow evaluation tasks

Keep this directory in the source release. Most users do not edit or run it during ordinary
analysis; maintainers and users validating an installation can run it with pytest.

```bash
uv sync --extra dev
uv run pytest
```

The first command synchronizes the Python environment and includes the optional `dev`
dependencies defined in `pyproject.toml`, such as pytest and lint tools. It does not install
pipeline datasets. The second runs pytest in the project environment; pytest discovers
`test_*.py` files under the configured test directory.

`conftest.py` provides shared temporary files, isolated test configuration, and helper
functions. Users do not replace its temporary paths with their own production server
configuration. Tests change when behavior, supported interfaces, or source versions change.

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

Schema tests check the consistency of packaged groups and exercise generation with a
small synthetic schema defined in the test itself. These checks do not establish full
coverage of an official pipeline release; that requires the matching authoring source
bundle. Tests of runner mechanics use mock agents and do not establish model quality.

## Two different kinds of evaluation input

| Location | Evaluated behavior | Main contents | Real Nextflow execution? |
| --- | --- | --- | --- |
| `pipeline_support/<pipeline>/` | Translate a task into a specified run, complete it, and produce required outputs | Visible task, hidden specification, localization plan/script | Needed for actual run-level scoring; not merely to validate these files |
| `skills/experts/<pipeline>-expert-skill/evals/` | Use a skill to answer planning, parameter, output/QC, and coverage questions | Questions, expected answers, assertions | No |

Within `pipeline_support/`, `smoke.task.md` is visible to the evaluated agent; `smoke.yaml`
is the hidden evaluation specification. `smoke.localization.yaml` and `localize_testdata.py`
describe and prepare local inputs. Keep hidden specifications out of the executing agent's
context when comparing skill and no-skill conditions.

`test_pipeline_support_contracts.py` checks these reusable definitions. It supports the
paper's method but is not an experiment log or a biological workflow. Keep it with the
task definitions. A deliberately minimal runtime-only distribution could omit both, but
the full source release should retain them for method reuse. Removing only the test leaves
the definitions without their consistency checks.

Some historical localization scripts still need upstream files and deployment-specific
paths; a clean source checkout is not a prepared biological test environment. Historical
run results are not included by retaining these task definitions.

## Directory naming

`tests/` is a convention, not a Python requirement. Renaming it would require updating
pytest `testpaths`, imports such as `tests.conftest`, fixture paths, task references,
documentation, and any automation. Keep the current name unless there is a concrete need.
