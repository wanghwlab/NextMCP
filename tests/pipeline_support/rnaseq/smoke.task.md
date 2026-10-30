# Task

Run the `rnaseq` pipeline on the prepared local dataset that is already
available on this server in project `pipeline-support-rnaseq`. Keep the
project-owned default results directory for this run.

## Available inputs

- Input samplesheet: `/data/rnaseq_test_data/samplesheet_test_local.csv`
- Reference bundle root:
  `/data/rnaseq_test_data/626c8fab639062eade4b10747e919341cbf9b41a/reference/`

## Route constraints

- Use project `pipeline-support-rnaseq`.
- Use the local reference bundle for the genome FASTA, annotation GTF and GFF,
  transcript FASTA, additional FASTA, BBSplit FASTA list, HISAT2 index, and
  Salmon index.
- Keep the standard STAR + Salmon analysis path.
- Keep BBSplit enabled.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.
