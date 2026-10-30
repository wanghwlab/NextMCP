# Playbooks

Use `assets/playbooks.yaml` and compose a route preset with confirmed server-local input,
output and references. For this official release the genome aligner is `star`.

For the requested combined rRNA + tRNA depletion workflow, use `bowtie2_rrna_removal`: set
`remove_ribo_rna=true`, `ribo_removal_tool=bowtie2`, and a confirmed `ribo_database_manifest`.
The manifest must cover both rRNA and tRNA for the intended organism, with one reference FASTA per line. `save_non_ribo_reads=true` saves retained
reads. Do not assume the default rRNA set also removes tRNA. `rrna_blacklist` applies to
novel transcript filtering, not FASTQ depletion. SortMeRNA remains the official default.

Ribo-TISH and RiboCode are default callers; Ribotricer, PRICE and Rp-Bp are opt-in.
Review read lengths, offsets and periodicity before treating their ORF calls as credible.
Matched RNA-seq/Ribo-seq TE requires a valid contrasts file and biological replication.
The default count definition is `te_quantification_method=plastid_psite`;
`alignment` and experimental `pseudo` are distinct choices. Do not mix their counts without
explicitly reconciling the analysis design. `skip_plastid` changes default TE behavior.

For extended ORFs, confirm canonical_gtf and a novel-transcript source before enabling
extended_orf_analysis. See `07_version_update.md` for StringTie, hybrid STAR alignment,
consensus catalogue, per-ORF counts and ORF-level differential translation requirements.

Preserve UMI position/pattern, BBSplit reference and saved-index compatibility checks from
the corresponding assets. Use `from_run_id` only after checking the historical launch_spec.
For a new run use pipeline `nf-core/riboseq` and extra_args `["-r", "2.0.0"]`.
After launch read run_get(include=["progress","artifact_summary","diagnosis","next_actions"]),
then run_artifacts and explicit files. This official package does not provide custom step entries.
