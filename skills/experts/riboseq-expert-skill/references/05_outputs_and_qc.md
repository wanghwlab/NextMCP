# Outputs and QC

Start with run_get(include=["progress","artifact_summary","diagnosis","next_actions"]),
then run_artifacts. Read only discovered report paths with fs_read. Use the official output
catalog in `assets/artifact-contracts.yaml` to identify the selected route's output family.

Review MultiQC and pipeline_info, reference identity, read retention and STAR mapping first.
For Bowtie2 depletion inspect `preprocessing/bowtie2_rrna/*.bowtie2.log`; retained FASTQs
are published there only with save_non_ribo_reads. Confirm the reference contains the
intended rRNA/tRNA targets rather than interpreting every filtered read as rRNA.
For combined rRNA + tRNA depletion, the alignment summary measures filtering against the
combined reference. Do not report separate rRNA and tRNA depletion rates unless additional
class-specific evidence supports them. Do not require SortMeRNA outputs for a Bowtie2 run.

Ribo-TISH and RiboCode QC/calls are under `riboseq_qc/` and `orf_predictions/`.
Ribotricer outputs require run_ribotricer=true. PRICE and Rp-Bp likewise require opt-in.
Inspect `psites/plastid/` and `psites/ribowaltz/` for offset inference and periodicity;
an exit status alone does not establish translation signal or biological validity.

`quantification/inframe_psite/` supplies default gene-level TE counts. Salmon alignment
counts and the experimental Salmon/Kallisto pseudo routes have different definitions.
Use `07_version_update.md` to check skip_plastid fallback behavior before comparing runs.
Review `translational_efficiency/anota2seq/` or `translational_efficiency/deltate/` as selected.
Check sample design and model diagnostics before interpreting significant results.

Extended analysis adds `orf_predictions/catalogue/`, its consensus view,
`quantification/orf_level/`, and `translational_efficiency/orf_level/` when enabled.
dotseq is ORF-level only. Multiple ORFs sharing a gene's RNA count are not independent
biological replicates. Review caller/sample support and host-gene mapping.

For historical reuse use run_list with a known artifact_path_contains fragment, then
run_get and run_artifacts. Treat artifacts.json and pipeline_fingerprint as recorded facts;
confirm source release, params and reference compatibility before reuse.
