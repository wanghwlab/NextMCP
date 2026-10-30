# Playbooks

Start from `assets/playbooks.yaml`. Choose the route from the user's input shape and analysis goal.

## Standard Samplesheet Run

Use `samplesheet_fastq` when the user has FASTQ data and a server-local samplesheet. Confirm `sampleID` and `forwardReads`; confirm `reverseReads` for paired-end data and `run` when error models must be separated by sequencing run. Set `FW_primer` and `RV_primer` unless the user confirms that reads do not contain primers and asks to use `skip_cutadapt`.

## Folder FASTQ Run

Use `folder_fastq` when files are already organized in one server-local folder. Confirm compressed FASTQ files and `extension`. Add `single_end`, `pacbio`, `iontorrent`, or `multiple_sequencing_runs` only when the data shape requires it.

## FASTA Taxonomy Run

Use `fasta_taxonomy_only` when ASV or OTU sequences were computed elsewhere. Choose a taxonomy route before launch. Most FASTQ denoising outputs will not be expected for this route.

## ITS And Variable-Length Amplicons

Use `variable_length_its` for ITS or other variable-length amplicons. `illumina_pe_its` changes read truncation behavior. `cut_its` asks ITSx to extract ITS1 or ITS2 before taxonomy.

## Multi-Region Sidle

Use `multiregion_sidle` when multiple 16S regions should be unified. Confirm a region file with `region`, `region_length`, `FW_primer`, and `RV_primer`, plus `sidle_ref_taxonomy` or custom Sidle reference files.

## Taxonomy Alternatives

Use `taxonomy_alternatives` when the user requests SINTAX, Kraken2, QIIME2, custom databases, a pre-trained QIIME2 classifier, or pplacer. If several taxonomy tools run, downstream QIIME2 receives one taxonomy by priority: pplacer, DADA2, SINTAX, Kraken2, then QIIME2.

## Metadata And Downstream Analysis

Use `downstream_metadata_analysis` when the user asks for barplots, diversity, ADONIS, ANCOM, ANCOM-BC, PICRUSt2, SBDI, or R objects. Confirm QIIME2-compatible metadata before promising those outputs.

## Historical Reuse

When the user remembers only an output name, use `run_list(project=..., pipeline="ampliseq", artifact_path_contains=...)`, then `run_get(include=["artifact_summary"])`, then `run_artifacts(...)`. Treat `artifacts.json` and `pipeline_fingerprint` as historical facts and confirm compatibility with `pipeline_info/params.json` before recommending reuse.
