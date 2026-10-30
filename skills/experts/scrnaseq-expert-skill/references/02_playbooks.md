# Playbooks

Start with `assets/playbooks.yaml`; this file explains the route choices in prose.

## Default Simpleaf

Use `simpleaf_default` when the user wants a normal barcode-based scRNA-seq analysis and has not requested another aligner. Confirm `input`, `outdir`, a concrete `protocol`, and either a server-local prebuilt Simpleaf index or reference inputs that can build one. The source workflow rejects `protocol=auto` for Simpleaf.

## STARsolo

Use `starsolo` for STARsolo matrices, pre-mRNA counts, RNA velocity matrices, or published STAR BAMs. Confirm `star_index` or FASTA/GTF, choose `star_feature`, and set `save_align_intermeds` only when the user needs BAM files.

## Kallisto/BUS

Use `kallisto_bus` for BUS outputs and Kallisto/Bustools matrices. Confirm `kallisto_index` or reference inputs, `txp2gene`, and `kb_workflow`. Keep `kb_workflow=standard` unless the user asks for `lamanno` or `nac`.

## Cell Ranger Routes

Use `cellranger` for 10x Cell Ranger count outputs. Confirm Cell Ranger availability on the server and a compatible `cellranger_index` or build inputs.

Use `cellrangerarc` for 10x Multiome ATAC + GEX. Confirm ARC-specific samplesheet columns and 10x-compatible FASTQ names.

Use `cellrangermulti` for Cell Ranger Multi with GEX plus VDJ, antibody capture, CRISPR, FFPE, CMO, or OCM data. Confirm the second barcode samplesheet for multiplexed samples and the route-specific reference files.

## CellBender And Reuse

Use `cellbender_filtering` when the user wants remove-background filtering and the aligner is not `cellrangerarc`.

Use `reference_build_or_reuse` when the user wants to save or reuse Simpleaf, STAR, Kallisto, Cell Ranger, Cell Ranger ARC, or Cell Ranger Multi references.

Use `historical_reuse` before rerunning when the user remembers a matrix, web summary, or report fragment. Search with `run_list(..., artifact_path_contains=...)`, then verify route compatibility through `pipeline_info/params.json`.
