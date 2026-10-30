# Task

Use the nextmcp server.
Run the localized `epitopeprediction` lightweight example in project
`pipeline-withskill-epitopeprediction`. Use the rewritten samplesheet that points
to two allele files and one shared peptide TSV. Every path listed below already
exists on the nextmcp server. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/epitopeprediction/test_peptides/rewrites/pipeline-data/testdata/sample_sheets/sample_sheet_peptides_local.csv`
- Human alleles file: `/data/nextmcp/testdata/epitopeprediction/test_peptides/pipeline-data/testdata/alleles/alleles.txt`
- Mouse alleles file: `/data/nextmcp/testdata/epitopeprediction/test_peptides/pipeline-data/testdata/alleles/alleles.H2.txt`
- Shared peptide file: `/data/nextmcp/testdata/epitopeprediction/test_peptides/pipeline-data/testdata/peptides/peptides.tsv`

## Workflow goal

- Run the peptide-to-binding-prediction route represented by the rewritten samplesheet.
- Keep the two-sample layout in which the human sample uses the human allele file and the mouse
  sample uses the mouse allele file.
- Use the shared peptide TSV for both samples.
- Use the MHCnuggets class I prediction path for short class I peptides of 9 to 10 amino acids.
- Keep the upstream test resource caps at 2 CPUs, 6.GB memory, and 48.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/epitopeprediction/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-epitopeprediction` as project name.
- Do not use the `epitopeprediction` expert skill.
