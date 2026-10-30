# Playbooks

Start with `assets/playbooks.yaml`. Choose one route, then read `assets/param-presets.yaml` and
the relevant schema group only when exact field mapping matters.

For a normal run, confirm `project`, `input`, `protocol`, and `outdir`. If inputs are already
per-sample FASTQ or BAM files, set `skip_demultiplexing=true`. If one pooled FASTQ needs qcat, set
`skip_demultiplexing=false`, provide `input_path`, and provide a supported `barcode_kit`.

For DNA variant calling, set `protocol=DNA` and `call_variants=true`. Choose `variant_caller`
among `medaka`, `deepvariant`, and `pepper_margin_deepvariant`. Choose
`structural_variant_caller` among `sniffles` and `cutesv`. Use `skip_vc` or `skip_sv` only when the
user wants one variant class. Confirm Docker/Singularity for DeepVariant or PEPPER routes, and GPU
capacity before using `deepvariant_gpu`.

For cDNA or directRNA quantification, keep `skip_quantification=false` and choose
`quantification_method=bambu` or `quantification_method=stringtie2`. Use
`skip_differential_analysis=true` when the user wants counts without DESeq2/DEXSeq. Check that the
samplesheet has usable FASTA and GTF values.

For direct RNA modification analysis, set `protocol=directRNA` and keep
`skip_modification_analysis=false`. The samplesheet `input_file` values should point to
server-local directories with `fast5` and `fastq` subdirectories. Use `skip_xpore` or `skip_m6anet`
to run only one modification tool.

For fusion analysis, use `protocol=cDNA` or `protocol=directRNA` and keep
`skip_fusion_analysis=false`. Provide `jaffal_ref_dir` when the server should use a prebuilt
reference; otherwise the workflow attempts to fetch and unpack the reference.

For historical reuse, search with `run_list(project=..., pipeline="nanoseq",
artifact_path_contains=...)`, inspect `run_get(include=["artifact_summary"])`, then use
`run_artifacts`. Treat `artifacts.json` and `pipeline_fingerprint` as historical facts, and read
`pipeline_info/params.json` before saying an old artifact is compatible.
