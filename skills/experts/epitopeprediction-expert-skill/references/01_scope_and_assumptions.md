# Scope And Assumptions

This package covers `nf-core/epitopeprediction` through nextmcp. It was generated from a
repository-local inspect-equivalent bundle rooted at
`/root/key_projects/nextmcp/nf_pipeline/epitopeprediction`, using `nextflow_schema.json`,
`README.md`, top-level docs, `main.nf`, `nextflow.config`, and
`workflows/epitopeprediction.nf`.

## Runtime Scope

Use this skill for epitope prediction from:

- annotated variant files: `.vcf` or `.vcf.gz`
- protein input: `.fasta` or `.fa`
- peptide tables: `.tsv` with the peptide column named by `peptide_col_name`, default `sequence`

The samplesheet must contain `sample`, `alleles`, `mhc_class`, and `filename`. MHC class values are
`I` and `II`. Alleles can be semicolon-separated values or a server-local text file with one allele
per row.

## Main Assumptions

- Variant input is already annotated with SnpEff or VEP.
- `mhcnuggets` is the default predictor.
- Valid predictor names are `mhcflurry`, `mhcnuggets`, `mhcnuggetsii`, `netmhcpan`, and
  `netmhciipan`.
- NetMHCpan and NetMHCIIpan require server-local licensed software tarballs.
- The current README states that `conda` and `mamba` profiles are not supported for this pipeline
  version. Prefer the server default profile unless the user gives a different runtime requirement.

## Path Boundary

All runtime `path` values, the `project` identifier, and relative path-like values in `params` or
`config_files` resolve on the nextmcp server filesystem. Do not pass client-local paths. Use paths
returned by nextmcp tools or paths the user confirmed exist on the server.

## Resource Overrides

Resource caps belong in a small server-local Nextflow config file passed through
`nextflow_run(config_files=[...])`. Use this syntax:

```groovy
process {
  resourceLimits = [
    memory: 64.GB,
    cpus  : 16,
    time  : 24.h
  ]
}
```
