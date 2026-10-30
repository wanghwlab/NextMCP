# NextMCP server configuration

This directory contains the YAML template and the private configuration used by the
NextMCP server. All deployment paths refer to the **analysis server**, not the client
computer running Codex or Claude Code.

| File | Purpose | Publish on GitHub? |
| --- | --- | --- |
| [config.example.yaml](config.example.yaml) | Editable configuration template | Yes |
| config.yaml | Actual deployment paths and authentication token | No; ignored by Git |
| README.md | Configuration reference and setup instructions | Yes |

The instructions below follow the current configuration loader and server implementation.
Connection instructions are consolidated in the [main README](../README.md#connect-a-client);
the legacy docs directory is not required.

## Create the private configuration

From the repository root on the server, after installing the project dependencies:

```bash
cp config/config.example.yaml config/config.yaml
command -v nextflow
```

Copy the template only for an initial setup; do not overwrite an existing deployment
configuration. Edit config/config.yaml before starting the service.

The shipped template and the example below use **127.0.0.1:8321**, enable bearer
authentication, and disable the optional local pipeline catalogue. Replace the token
placeholder and all deployment paths before starting the service.

Replace every /srv/ path with an absolute server path, set executable to the actual
Nextflow executable, and replace the token placeholder.

```yaml
server:
  host: 127.0.0.1
  port: 8321
  base_dir: /srv/nextmcp
  logging_level: INFO
  reload_config_on_change: false
  reload_config_interval_seconds: 1.0

auth:
  enabled: true
  bearer_token: "REPLACE_WITH_A_LONG_RANDOM_TOKEN"

paths:
  allowed_read_roots:
    - /srv/nextmcp
    - /srv/data
    - /srv/references
  allowed_write_roots:
    - /srv/nextmcp

state:
  db_path: /srv/nextmcp/state/processes.db

projects:
  root: /srv/nextmcp/projects

audit:
  file_path: /srv/nextmcp/logs/audit.log
  max_bytes: 5242880
  backup_count: 3

nextflow:
  executable: /absolute/path/to/conda/envs/nextmcp/bin/nextflow
  pipeline_roots: []
  default_profile: docker
  igenomes_ignore: false
  expose_pipeline_materials: false
  env:
    NXF_HOME: /srv/nextmcp/.nextflow
    NXF_OFFLINE: "false"
    NXF_VER: "25.10.2"
```

Generate a token on your own machine, then place it in the private configuration and
provide it securely to the intended client:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

Use YAML booleans for configuration switches, but strings for environment-variable
values. Use absolute paths rather than ~ or shell expressions such as ${HOME};
the configuration loader does not perform shell expansion or environment substitution.
Keep indentation consistent and use spaces.

## Field reference

### Server and authentication

| Field | Meaning |
| --- | --- |
| server.host | Listening address. 127.0.0.1 accepts connections on the server itself; 0.0.0.0 listens on all IPv4 interfaces |
| server.port | HTTP listening port; the MCP endpoint is /mcp on that port |
| server.base_dir | Present in the configuration model, but the current runtime does not use it to derive project, database, or log paths |
| server.logging_level | Application log level, normally INFO |
| server.reload_config_on_change | Enable request-driven configuration reload; false means restart to load edits |
| server.reload_config_interval_seconds | Minimum interval between reload checks, in seconds; must be nonnegative |
| auth.enabled | Require the configured static bearer token when true |
| auth.bearer_token | Token expected in Authorization: Bearer TOKEN; must be nonempty when authentication is enabled |

Changing base_dir alone does not relocate any data. Set projects.root, state.db_path,
audit.file_path, and the allowed paths explicitly.

Authentication is a service access check, not a per-user project permission system.
Clients using the same service access its shared configured projects and run records.
The token does not replace the SSH account password, and SSH authentication does not
replace the MCP token.

### Paths, projects, state, and audit

| Field | Meaning |
| --- | --- |
| paths.allowed_read_roots | Nonempty list of directories permitted by NextMCP's read-path checks |
| paths.allowed_write_roots | Nonempty list of directories permitted by NextMCP's write-path checks |
| state.db_path | SQLite database for process/run tracking; its parent must be under an allowed write root |
| projects.root | Parent directory for analysis projects; must be under an allowed write root |
| audit.file_path | Audit log destination; its parent must be under an allowed write root. An empty string disables the dedicated audit file sink |
| audit.max_bytes | Audit file rotation threshold in bytes; must be positive. 5242880 is 5 MiB |
| audit.backup_count | Number of rotated audit files to retain; must be nonnegative |

If projects.root is omitted or unset, the effective location is
<allowed_write_roots[0]>/projects. Database and audit paths are configured separately.

Read and write permissions are separate. Include result directories in allowed_read_roots
when the client needs to inspect them. These settings do not grant Linux filesystem
permissions: the service account must also be able to access the files. Path checks
restrict NextMCP operations; they do not sandbox every action performed by workflow code.

With the example configuration, projects and results are stored under /srv/nextmcp/projects,
the tracking database under /srv/nextmcp/state, and the audit log under /srv/nextmcp/logs.
These generated files are deployment state, not source files to publish.

### Nextflow

| Field | Meaning |
| --- | --- |
| nextflow.executable | Nextflow command or absolute executable path. An absolute path avoids dependence on the service's PATH |
| nextflow.pipeline_roots | List of directories used for local pipeline discovery; [] disables the catalogue |
| nextflow.default_profile | Default workflow profile, such as docker; a request can supply its own profile. null means no default profile |
| nextflow.igenomes_ignore | When true, generate a Nextflow config setting igenomes_ignore=true and igenomes_base=/tmp/igenome_tmp |
| nextflow.expose_pipeline_materials | Permit nextflow_inspect_pipeline and additional source/schema metadata in local discovery responses |
| nextflow.env | Environment values supplied to Nextflow launches; request-specific values override matching configured values |

Selecting docker does not install Docker. Install and configure a container runtime that
the chosen workflow profile supports. The Nextflow executable, Java, plugins, containers,
inputs, and reference data must be usable by the account running NextMCP.

The igenomes_ignore setting is a server-wide parameter override. The runtime writes
nextmcp-igenomes.config beside the process database and passes it with -c. These
values therefore appear in the generated config rather than the prepared params mapping. It does not download or
find reference files, and it replaces conflicting request values for those two parameters.
Use it only with compatible pipelines. When false, NextMCP does not apply that override;
it does not mean every run will download iGenomes data.

The example environment specifies a Nextflow home directory and a launcher version.
NXF_OFFLINE controls Nextflow's offline behavior, not NextMCP's model-based skill evaluation.
Setting it does not prepare missing workflow code, plugins, containers, or datasets.
Consult the [Nextflow environment reference](https://docs.seqera.io/nextflow/reference/env-vars)
for the installed release's behavior.

## Run without nf_pipeline

For remote workflow identifiers, use:

```yaml
nextflow:
  pipeline_roots: []
  expose_pipeline_materials: false
```

This is a fragment to merge into the existing nextflow section, not a second nextflow
section to append. Omitting pipeline_roots also uses the code default of an empty list;
keeping [] makes the choice explicit.

Use an explicit identifier such as nf-core/rnaseq and pin its release in the execution
request, for example extra_args: ["-r", "3.22.2"]. No vendored nf_pipeline directory is
required for this mode. Nextflow resolves the workflow using its own retrieval/cache
mechanism; the required workflow and dependencies must still be available.

With an empty catalogue, nextflow_list_pipelines returns an error indicating that
pipeline_roots is empty; it does not list the online nf-core catalogue. This is not an
authentication failure. Optional NextMCP parameter-schema validation requires a local
schema, so do not enable validate_params_schema for a remote-only target.

## Enable local pipeline materials when needed

For optional local discovery or expert-skill authoring, configure existing checkouts:

```yaml
nextflow:
  pipeline_roots:
    - /srv/pipelines
  expose_pipeline_materials: true
```

For example, /srv/pipelines may contain rnaseq/ and sarek/ checkouts. These directories
contain workflow code and documentation; pipeline_roots is not a samplesheet path,
a single YAML filename, or a list of installed client skills.

The local catalogue has its own path access rules. Its roots do not have to be added to
allowed_read_roots solely for catalogue discovery and inspection. General fs_read access
still follows the normal read-path checks.

When expose_pipeline_materials is false, nextflow_inspect_pipeline returns feature_disabled
for both summary and materials requests. Local discovery can still identify pipelines if
roots are configured, but does not expose repository paths or schema-derived metadata.
When enabled, inspection returns the currently deployed local materials. It does not
fetch the latest website content or upgrade the checkout.

Enabling this flag does not generate, install, or update an expert skill. See the
[skill authoring guide](../skills/meta/README.md#generate-or-update-an-expert-skill).

## Validate, inspect, and start

Create the directories for your chosen configuration and keep the private YAML readable
only by the intended service account. For the example above:

```bash
mkdir -p /srv/nextmcp/state /srv/nextmcp/projects /srv/nextmcp/logs /srv/nextmcp/.nextflow
chmod 600 config/config.yaml
uv run nextmcp --config config/config.yaml --check-config
uv run nextmcp --config config/config.yaml --dump-config
uv run nextmcp --config config/config.yaml
```

The input and reference directories must already contain the intended data.
--check-config and --dump-config do not start the HTTP server or launch Nextflow, but
they initialize runtime helpers and may create directories, logs, and the SQLite database
or reconcile existing tracking records. They are not purely read-only YAML syntax checks.

The dump redacts sensitive keys, including the bearer token. It can still contain private
deployment paths, so review it before sharing. A successful configuration check does not
prove that Nextflow, a container engine, input data, or an analysis is ready.

Configuration file selection follows this order:

1. Explicit --config path.
2. NEXTMCP_CONFIG environment variable.
3. config.yaml in the current working directory.

The fallback is not config/config.yaml. Use --config explicitly to avoid loading the
wrong file. The current loader falls back to code defaults when a file is missing, and
ignores unknown configuration keys; do not rely on it to catch every filename or spelling
mistake. CLI --host and --port can override the listener settings.

## Apply configuration changes

With reload_config_on_change: false, restart the service after editing the YAML.
Changing the file alone does not update the running service.

When reload is enabled, incoming requests trigger modification-time checks, throttled
by reload_config_interval_seconds. Successful reloads replace runtime helpers for new
requests; they do not rewrite already launched jobs. Failed reloads are logged and the
previous active configuration remains in use.

Hot reload does not rebind the HTTP listener or reconfigure startup logging. Restart for
host, port, or logging-level changes. Enable reload through a restart if the running
configuration currently has it disabled. Plan changes to database or project roots as
data-location changes, not as automatic migration.

After changing a token, update the clients too. After changing material access, verify
the reported pipeline_materials.enabled value with server_info.

## Connect the client

For this example, keep the server running and establish the tunnel on the client computer:

```bash
ssh -N -T -p 22 -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -L 127.0.0.1:8321:127.0.0.1:8321 USER@SERVER
```

Replace USER and SERVER. This command also works directly in Windows PowerShell.
Keep the SSH window open. A successful -N connection normally does not display a remote
shell prompt. The client's MCP endpoint is then http://127.0.0.1:8321/mcp.

| Item | Where it belongs |
| --- | --- |
| SSH account/password or key | The SSH connection on the client |
| Server bearer_token | The MCP authentication configuration on the client |
| Server YAML | The analysis server |
| Codex/Claude Code MCP registration | The client computer |
| Expert skill installation | The client computer |
| Samplesheets, reads, references, and outputs | Server-accessible locations |

Follow the [Codex or Claude Code connection steps](../README.md#connect-a-client) to
register the URL and token. The tunnel forwards requests; it does not synchronize local
files or map Windows drive letters to Linux paths.

Finally, ask the client agent:

```text
Call nextmcp server_info without arguments.
Report readiness and any blocking issues. Do not launch an analysis.
```

A successful tool call confirms connectivity and authentication. Readiness is a separate
check of the reported server prerequisites, not a guarantee that a particular pipeline
will finish.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| HTTP 401 | The client has the server's active bearer token, not the SSH password |
| Connection refused | The service and SSH process are running and their ports agree |
| Configuration appears unchanged | Check the explicit --config path and restart/reload behavior |
| Read/write denied | Check server paths, the corresponding allowed roots, and OS permissions |
| state.db_path or projects.root fails validation | Place it under an allowed write root or update that root |
| Local catalogue unavailable | Expected with pipeline_roots: []; use an explicit remote identifier |
| feature_disabled during inspection | Enable material exposure and configure local roots if authoring requires it |
| Nextflow executable not found | Use the service account's real executable path and environment |
| Container launch fails | Verify the selected profile and installed container runtime |
| Setting base_dir does not move outputs | Set projects.root and other storage paths explicitly |

## Implementation references

- [Configuration fields and validation](../src/nextmcp/config.py)
- [CLI configuration selection and startup](../src/nextmcp/cli.py)
- [Runtime reload behavior](../src/nextmcp/runtime_state.py)
- [Authentication middleware](../src/nextmcp/server.py)
- [Pipeline discovery and inspection tools](../src/nextmcp/tools/nextflow_tools.py)

