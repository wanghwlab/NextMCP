# nf-core/riboseq 2.0.0: source and update notes

Source: https://nf-co.re/riboseq/2.0.0/
Exact code: https://github.com/nf-core/riboseq/tree/2.0.0

## Analysis choices and interpretation

- The genome aligner is star (the only aligner enum). Do not use the rnaseq value star_salmon. The main workflow still uses STAR and Salmon where specified by the chosen quantification route.
- For the requested Bowtie2 depletion route, set remove_ribo_rna=true, ribo_removal_tool=bowtie2 and ribo_database_manifest to a server-confirmed text file containing one reference FASTA path per line. Bowtie2 keeps unaligned reads for downstream analysis. save_non_ribo_reads=true publishes the retained FASTQs.
- The official default ribo_removal_tool is sortmerna, not bowtie2. Bowtie2 here is an explicit user-selected preset. The official feature is rRNA removal: tRNA removal additionally requires appropriate tRNA sequences in the supplied reference set; the default rRNA manifest does not establish tRNA coverage. For this requested route, rtRNA means rRNA + tRNA; verify that the supplied references cover both classes.
- The riboseq 2.0.0 schema does not expose rnaseq's bowtie2_rrna_index parameter. Do not pass sortmerna_index as a Bowtie2 index. rrna_blacklist is a BED filter for novel transcripts and is not the FASTQ rRNA-removal reference.
- Review preprocessing/bowtie2_rrna/*.bowtie2.log, retained read counts and MultiQC. High depletion can indicate contamination or an unsuitable reference; interpret it with downstream mapping and periodicity rather than assuming a successful run implies good Ribo-seq signal.
- Default ORF callers include Ribo-TISH and RiboCode. Ribotricer is opt-in through run_ribotricer; skip_ribotricer was removed. PRICE and Rp-Bp are also opt-in through run_price and run_rpbp and add substantial computation. Treat Ribotricer score rankings cautiously as described by the release.
- te_quantification_method defaults to plastid_psite. alignment selects STAR-to-Salmon counts; pseudo selects the experimental direct transcriptome route. pseudo_aligner=salmon or kallisto applies only to pseudo, not to the primary STAR alignment. Single-end Kallisto requires kallisto_quant_fraglen and kallisto_quant_fraglen_sd.
- skip_plastid disables per-ORF P-site quantification and makes the default plastid_psite gene-level TE route fall back to alignment-based counts. Do not compare these counts across runs as if their definitions were unchanged.
- translational_efficiency_method is a comma-separated selection of anota2seq, deltate and dotseq; default anota2seq. dotseq is ORF-level only and requires extended_orf_analysis=true. Confirm matched rnaseq/riboseq samples, contrasts and biological replication before interpreting differential translation.
- Extended ORF analysis uses canonical_gtf and a novel transcript source: novel_gtf or RNA-seq-driven StringTie with skip_stringtie=false. The hybrid reference supports a second STAR pass and a cross-caller ORF catalogue. Review orf_min_callers, orf_min_samples and smorf_max_aa before interpreting consensus and peptide collapse.
- Review psites/plastid/ and psites/ribowaltz/ for offsets and periodicity, quantification/inframe_psite/ for default TE counts, orf_predictions/catalogue/ for the union and consensus, and quantification/orf_level/ for ORF counts. ORFs sharing a host-gene RNA denominator are not statistically independent biological replicates.
- equalise_read_lengths optionally trims RNA-seq reads for alignment-based TE comparisons. It is a deliberate analysis choice, not an automatic prerequisite. The official tag has no project-specific interactive.nf or STEP_* interface.

## Parameter migration

Use assets/schema-index.yaml and its grouped files for exact defaults, enums, constraints and descriptions.

Added parameters: `canonical_gtf`, `equalise_read_lengths`, `equalise_read_lengths_target`, `extended_orf_analysis`, `extra_deltate_args`, `extra_dotseq_args`, `extra_kallisto_quant_args`, `extra_orf_anota2seq_run_args`, `extra_orf_deltate_args`, `extra_plastid_make_wiggle_args`, `extra_plastid_metagene_generate_args`, `extra_plastid_psite_args`, `extra_price_indexgenome_args`, `extra_price_price_args`, `extra_ribocode_gtfupdate_args`, `extra_ribocode_metaplots_args`, `extra_ribocode_prepare_args`, `extra_ribocode_ribocode_args`, `extra_ribowaltz_args`, `extra_rpbp_predictorfs_args`, `extra_rpbp_preparegenome_args`, `extra_stringtie_args`, `extra_stringtie_merge_args`, `fastp_merge`, `gffcompare_class_codes`, `help`, `help_full`, `kallisto_index`, `kallisto_quant_fraglen`, `kallisto_quant_fraglen_sd`, `novel_gtf`, `orf_min_callers`, `orf_min_samples`, `plastid_default_psite_offset`, `plastid_max_length`, `plastid_min_length`, `pseudo_aligner`, `ribo_lfc_threshold`, `ribo_removal_tool`, `ribodetector_chunk_size`, `rna_lfc_threshold`, `rrna_blacklist`, `run_price`, `run_ribotricer`, `run_rpbp`, `show_hidden`, `skip_coverage_tracks`, `skip_orf_collapse`, `skip_plastid`, `skip_ribocode`, `skip_ribowaltz`, `skip_stringtie`, `smorf_max_aa`, `te_lfc_threshold`, `te_quantification_method`, `translational_efficiency_method`, `umitools_dedup_primary_only`

Changed type/default/enum: `pseudo_aligner_kmer_size`

Removed parameters: `hook_url`, `min_mapped_reads`, `skip_alignment`, `skip_ribotricer`

Do not pass removed parameters to this release. An absent schema default is not proof of a false or null runtime value; consult the pinned configuration when needed.

## Outputs and QC

Read assets/artifact-contracts.yaml for curated output rules and the exact-tag official_output_catalog. Start with run_get(include=["progress","artifact_summary","diagnosis","next_actions"]), then run_artifacts, and only then fs_read on discovered files. Read assets/qc-rules.yaml and the route-specific caveats above. No universal QC cutoff is implied.

## Provenance and scope

The schema and source archive checksums are recorded in assets/source-provenance.yaml. These assets were refreshed from the requested official tag, not from a moving latest/dev page or a server's customized checkout. Static validation and offline planning evaluation do not establish successful execution on a particular server.
