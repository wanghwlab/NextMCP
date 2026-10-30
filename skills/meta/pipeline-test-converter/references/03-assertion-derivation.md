# Assertion Derivation

## Principle

Do not try to reproduce the full nf-test snapshot.

Build a small stable assertion set that is suitable for batch smoke evaluation.

## Preferred assertion types

1. Run completes successfully
2. One or more key output paths exist
3. One or two anchor content checks succeed

## Evidence sources

Use:

- `tests/*.nf.test`
- `tests/*.snap`
- `tests/.nftignore`

## How to reduce snapshot material

When `.snap` is rich:

- choose top-level output directories
- choose one representative report or table
- ignore files clearly marked unstable in `.nftignore`

When `.nf.test` has explicit assertions:

- prefer those over broad snapshot lists

Example reductions:

- `fetchngs`
  - samplesheet exists
  - one fastq exists
  - one metadata file exists
- `riboseq`
  - one alignment directory exists
  - one QC or quantification anchor file exists
- `epitopeprediction`
  - one prediction directory exists
  - one merged result file exists

## What to avoid

- asserting every file in a large snapshot
- comparing volatile logs
- asserting tool version text unless the evaluation specifically needs that
