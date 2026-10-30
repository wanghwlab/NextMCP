# NextMCP server configuration

This directory contains the YAML template and the private configuration used by the
NextMCP server. All deployment paths refer to the **analysis server**.

| File | Purpose |
| --- | --- |
| [config.example.yaml](config.example.yaml) |Editable configuration template |
| README.md | Configuration reference and setup instructions |

The instructions below follow the current configuration loader and server implementation.
Connection instructions are consolidated in the [main README](../README.md#connect-a-client).

## Create the private configuration

From the repository root on the server, after installing the project dependencies:

```bash
cp config/config.example.yaml config/config.yaml
command -v nextflow
```

Edit config/config.yaml before starting the service.

The shipped template and the example below use **127.0.0.1:8321**, enable bearer
authentication, and disable the optional local pipeline catalogue. Replace the token
placeholder and all deployment paths before starting the service.

Replace every /srv/ path with an absolute server path, set executable to the actual
Nextflow executable, and replace the token placeholder.

Generate a token on your own machine, then place it in the private configuration and
provide it securely to the intended client:

```bash
# Generate a bearer_token 
python -c 'import secrets; print(secrets.token_hex(32))'
```

Use YAML booleans for configuration switches, but strings for environment-variable
values. Use absolute paths.

## Field reference

### Server and authentication

| Field | Meaning |
| --- | --- |
| server.host | Listening address. 127.0.0.1 accepts connections on the server itself |
| server.port | HTTP listening port |
| server.base_dir | Present in the configuration model |
| server.logging_level | Application log level |
| server.reload_config_on_change | Enable request-driven configuration reload; false means restart to load edits |
| server.reload_config_interval_seconds | Minimum interval between reload checks; must be nonnegative |
| auth.enabled | Require the configured static bearer token when true |
| auth.bearer_token | Token expected in Authorization: Bearer TOKEN; must be nonempty when authentication is enabled |

### Paths, projects, state, and audit

| Field | Meaning |
| --- | --- |
| paths.allowed_read_roots | Nonempty list of directories permitted by NextMCP's read-path checks |
| paths.allowed_write_roots | Nonempty list of directories permitted by NextMCP's write-path checks |
| state.db_path | SQLite database for process/run tracking |
| projects.root | Parent directory for analysis projects |
| audit.file_path | Audit log destination |
| audit.max_bytes | Audit file rotation threshold in bytes |
| audit.backup_count | Number of rotated audit files to retain |

Read and write permissions are separate. Include result directories in allowed_read_roots
when the client needs to inspect them.

### Nextflow

| Field | Meaning |
| --- | --- |
| nextflow.executable | Nextflow command or absolute executable path |
| nextflow.pipeline_roots | List of directories used for local pipeline discovery |
| nextflow.default_profile | Default workflow profile, such as docker |
| nextflow.expose_pipeline_materials | Permit nextflow_inspect_pipeline and additional source/schema metadata in local discovery responses |
| nextflow.env | Environment values supplied to Nextflow launches |

Consult the [Nextflow environment reference](https://docs.seqera.io/nextflow/reference/env-vars)
for the installed release's behavior.

## Validate, inspect, and start

Create the directories for your chosen configuration and keep the private YAML readable
only by the intended service account. 

```bash
mkdir -p /srv/nextmcp/state /srv/nextmcp/projects /srv/nextmcp/logs /srv/nextmcp/.nextflow
# Validate config only
uv run nextmcp --config config/config.yaml --check-config
# Print effective config with secrets redacted
uv run nextmcp --config config/config.yaml --dump-config
# Run
uv run nextmcp --config config/config.yaml
```
Use --config explicitly to avoid loading the
wrong file. 
