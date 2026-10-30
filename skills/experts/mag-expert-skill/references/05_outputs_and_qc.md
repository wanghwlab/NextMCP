# Outputs and QC

Start post-run review with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`.
Then call `run_artifacts(...)` for the relevant section. Use `fs_read` only after a concrete
server-local file path is known.

The first files to inspect for most completed runs are `multiqc/multiqc_report.html`,
`GenomeBinning/bin_summary.tsv`, `GenomeBinning/QC/`, `Taxonomy/GTDB-Tk/gtdbtk_summary.tsv`,
`Taxonomy/CAT/bat_summary.tsv`, and `pipeline_info/params.json`.

`GenomeBinning/bin_summary.tsv` is the main MAG summary table. It combines depth, quality,
taxonomy, and ancient DNA metrics when those stages ran. Use it before reading many per-bin files.

Use `GenomeBinning/QC/` for BUSCO, CheckM, CheckM2, GUNC, and QUAST summaries. High-quality
decisions should compare completeness, contamination, chimerism, and assembly metrics instead of
using one table alone.

Use `Taxonomy/GTDB-Tk/gtdbtk_summary.tsv` for GTDB-Tk classifications and failed or filtered
genomes. Use `Taxonomy/CAT/bat_summary.tsv` for CAT bin taxonomy. If `cat_classify_unbinned` was
enabled, CAT also publishes unbinned contig classification files.

Use `Annotation/Prokka/` for prokaryotic annotation and `Annotation/MetaEuk/` for eukaryotic or
unclassified bins when a MetaEuk database was supplied.

Use `Ancient_DNA/` only when `ancient_dna` was true. For reproducible pyDamage output, check that
`binning_map_mode` was `own`. Use `GenomeBinning/QC/pydamage_bins_summary.tsv` for bin-level damage
summaries.

Use `GenomeBinning/BIgMAG/bigmag_summary.tsv` when the user wants BIgMAG. If the file is missing,
check whether `generate_bigmag_file`, `run_busco`, `run_checkm2`, `run_gunc`, and GTDB-Tk were all
active.
