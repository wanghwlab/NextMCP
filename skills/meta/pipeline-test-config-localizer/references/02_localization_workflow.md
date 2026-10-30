# Localization Workflow

Follow this order. Do not start by drafting the final prompt.

## 1. Parse the config

Extract only assigned values that affect the test run.

Priority order:

- string assignments inside `params { ... }`
- high-signal config-level runtime hints such as `process.resourceLimits`
- comments that clarify the intended scale or dataset, but not decorative banner text

Before you download anything, resolve config precedence correctly:

- start from the exact file the user named
- follow ordinary pipeline runtime includes and defaults such as `nextflow.config`
- keep nf-test harness files out of scope unless the task is explicitly about reproducing nf-test

This matters when both of these exist:

- pipeline runtime default: `nextflow.config`
- test harness override: `tests/nextflow.config` or `nf-test.config`

For a nextmcp runtime task derived from `conf/test.config`, the pipeline runtime default is the
base value. The nf-test override is not the default source of truth.

For `riboseq/conf/test.config`, the direct download inventory begins with:

- `samplesheet.csv`
- `contrasts.csv`
- `rrna-db.txt`
- `Homo_sapiens.GRCh38.dna.chromosome.20.fa.gz`
- `Homo_sapiens.GRCh38.111_chr20.gtf`

## 2. Choose the server-local root

Use `server_info()` or a user-confirmed path to pick an allowed write root.

Use two path classes, in this order:

1. Preferred mapped mirror roots for known remote prefixes.
2. Fallback writable task-local root for unmatched URLs and rewritten manifests.

Treat the preferred mapped mirror root as a first attempt, not as a final answer.
If the mapped file is missing, continue with a task-local download unless the user
explicitly marked that mirror as authoritative.

Preferred mapping rule:

`<known local root> + <URL suffix after the matched remote prefix>`

Example:

`https://raw.githubusercontent.com/nf-core/test-datasets/epitopeprediction/testdata/sample_sheets/sample_sheet_variants_local.csv`

with

`https://raw.githubusercontent.com/nf-core/test-datasets/ -> /data/test-datasets/`

becomes:

`/data/test-datasets/epitopeprediction/testdata/sample_sheets/sample_sheet_variants_local.csv`

Another preferred mapping:

`s3://ngi-igenomes/igenomes/Homo_sapiens/GATK/GRCh38/Annotation/Sentieon/SentieonDNAscopeModel1.1.model`

with

`s3://ngi-igenomes/igenomes/ -> /data/igenomes/`

becomes:

`/data/igenomes/Homo_sapiens/GATK/GRCh38/Annotation/Sentieon/SentieonDNAscopeModel1.1.model`

If no prefix rule matches, use this fallback pattern:

`<server_input_root>/testdata/<pipeline>/<profile_name>/downloads/<host>/<remote path>`

This keeps the host and remote path visible for the small set of URLs that still
need downloading.

Fallback example:

`https://raw.githubusercontent.com/nf-core/test-datasets/riboseq/samplesheet/samplesheet.csv`

becomes:

`<server_input_root>/testdata/riboseq/test/downloads/raw.githubusercontent.com/nf-core/test-datasets/riboseq/samplesheet/samplesheet.csv`

## 3. Download the direct assets

Do not download every URL blindly.

For each URL:

- first try the known prefix map
- use the longest matching remote prefix if several mappings match
- keep the remaining suffix path exactly as it appears in the URL
- if the mapped target exists, reuse it
- if the mapped target is missing, download into the current `localized_root`
- do not stop with "missing expected local mirror" as the default behavior
- download only when no usable mapped target exists

Choose the fallback download command by scheme:

- `https://` or `http://`: prefer `curl -L --fail -o <target> <url>`, else `wget -O <target> <url>`
- `s3://`: prefer `aws s3 cp <url> <target>`, else `s5cmd cp <url> <target>`

For a directory-like remote prefix, switch to the recursive form only when the
config really needs the whole directory tree:

- `wget --recursive ...`
- `aws s3 cp --recursive ...`
- `s5cmd cp --recursive ...`

If none of the scheme-specific fetch tools exist, stop and report the missing
tool explicitly.

Do not flatten unmatched downloads into one directory. Mirror the upstream directory structure
instead.

For the final contract, prefer the paths inside the current localized bundle. Do
not default to a contract that points at a shared mirror root unless that
shared mirror was declared authoritative for the task.

If you emit a helper script such as `localize_testdata.py`, it should print
progress as it runs:

- log downloads and reuse decisions as they happen
- log when the script starts rewriting a local manifest
- log a final success line after the rewrite finishes
- prefer stderr for progress so stdout can stay reserved for the final rewritten manifest path

## 4. Inspect structured text for nested URLs

After each structured text file lands locally, inspect it for nested remote
URLs.

Typical recursive cases:

- samplesheets where FASTQ columns contain URL values
- manifest TXT files where each line is a remote reference URL
- CSV or TSV cells that contain semicolon-joined URL lists

Rules:

- apply the same prefix-map-first rule to nested URLs
- rewrite only data cells that are real URLs
- keep headers and non-URL cells unchanged
- if one file references many nested files, download them all before writing the rewritten manifest

## 5. Emit sibling local manifests

Keep the original file and write a rewritten local copy:

- `samplesheet.csv` -> `samplesheet_local.csv`
- `rrna-db.txt` -> `rrna-db_local.txt`

Example rewrite: samplesheet.csv -> `samplesheet_local.csv`

If the source file is inside a writable fallback download tree, write the `_local`
file next to it.

If the source file came from a mapped mirror root that should stay unchanged,
write the `_local` file under:

`<server_input_root>/testdata/<pipeline>/<profile_name>/rewrites/`

while preserving enough relative structure to keep the source clear.

The rewritten file should point only at server-local paths.

## 6. Capture mapping facts

Keep a small machine-readable or structured note for the runtime agent:

- config field name
- original remote value
- localization mode: `prefix_map` or `fallback_download`
- fetch method when a download was required
- localized server-local value
- official pipeline param name to send in `nextflow_run(params=...)`, or the
  server-local override config file and assignment when the value must stay in
  config scope

For `max_cpus`, `max_memory`, and `max_time`, prefer an override config entry
such as:

- `params.max_cpus = 2`
- `params.max_memory = '6.GB'`
- `params.max_time = '6.h'`

and pass that config file through `nextflow_run(config_files=...)`.

This keeps the main prompt natural while still making the launch deterministic.
