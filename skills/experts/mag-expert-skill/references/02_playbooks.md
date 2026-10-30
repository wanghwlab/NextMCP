# Playbooks

Start with `assets/playbooks.yaml`; this reference explains the route choices in plain language.

For a normal run, confirm `project`, `input`, and `outdir`. The samplesheet must be server-local and
must describe short reads, long reads, or both. Use `single_end` only when short reads are
single-end. By default, nf-core/mag assembles samples individually and uses the `group` column for
co-binning. Use `coassemble_group` only when the user wants group-wise co-assembly too.

For pre-computed assemblies, pass both `input` and `assembly_input`. The assembly CSV must have
`id`, `group`, `assembler`, and `fasta`. This route skips read preprocessing and assembly, then
continues at binning. Reads are still needed for depth estimation and downstream binning behavior.

For long-read-only data, confirm `long_reads` and `long_reads_platform` in the samplesheet. Choose
Flye and/or MetaMDBG through the skip flags when the user wants a single assembler. Confirm
`longread_adaptertrimming_tool` and `longread_filtering_tool` if the defaults are not acceptable.

For ancient DNA, set `ancient_dna: true`. Prefer `binning_map_mode: own` when reproducibility of
pyDamage output matters. Keep `skip_ancient_damagecorrection` false unless the user does not want
FreeBayes and BCFtools consensus recall.

For database-backed QC and taxonomy, confirm database paths before launch or explicitly accept a
download/generate route. CAT and GTDB-Tk databases are large. BUSCO offline mode requires the
requested lineage to exist under the supplied `busco_db`. `metaeuk_db` and `metaeuk_mmseqs_db` are
alternative routes and should not be used together.

For BIgMAG output, set `generate_bigmag_file: true`, keep `run_busco: true`, set
`run_checkm2: true`, set `run_gunc: true`, and do not skip GTDB-Tk. Review
`GenomeBinning/BIgMAG/bigmag_summary.tsv` after completion.

For historical reuse, search with `run_list(project=..., pipeline="mag",
artifact_path_contains=...)` using a known fragment such as `GenomeBinning/bin_summary.tsv`,
`Taxonomy/GTDB-Tk/gtdbtk_summary.tsv`, or `pipeline_info/params.json`. Then read
`run_get(include=["artifact_summary"])`, inspect `run_artifacts(...)`, treat `artifacts.json` and
`pipeline_fingerprint` as historical facts, and confirm route compatibility through
`pipeline_info/params.json`.
