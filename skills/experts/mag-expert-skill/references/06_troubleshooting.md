# Troubleshooting

Use summary-first browsing. Start with
`run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`, then use
`run_logs` only when the summary does not explain the failure. Use `fs_read` for explicit log or
output files after their server-local paths are known.

For samplesheet failures, check that the CSV is server-local, has the required columns, uses
compressed FastQ files, and does not mix paired-end and single-end short reads in one run. If
single-end short reads are used, set `single_end: true`.

For missing database errors, confirm the exact server-local path with `fs_list(mode="manifest")`.
Large databases may take a long time to download. Prefer stable server-local copies for CAT,
GTDB-Tk, BUSCO, CheckM, CheckM2, GUNC, geNomad, and MetaEuk. BUSCO offline mode needs the requested
lineage under the supplied `busco_db`.

Do not block a normal run on `checkm_db` or `checkm2_db`; run_checkm=false and run_checkm2=false in
the default route, so the default route does not need them. Require those database paths only when
the user enables CheckM or CheckM2.

For GTDB-Tk inode or file-count problems, use the documented SquashFS workaround only with
Apptainer or Singularity. Put the `withName: GTDBTK_CLASSIFYWF { containerOptions = ... }` override
in a small server-local config file and pass it through `config_files`.

For low or zero bin depths, check whether reads match assemblies and whether
`shortread_percentidentity` or `longread_percentidentity` is too strict. Older ONT data may need a
lower long-read percent identity.

For DAS Tool notes with ignored errors, explain that DASTool may not produce files when bins do not
pass refinement criteria. Consider `refine_bins_dastool_threshold` only after checking the binning
outputs.

For ancient DNA rerun differences, check `binning_map_mode`. The pipeline docs recommend `own` for
reproducible pyDamage results unless co-binning is required.

For restart planning, use `nextflow_run(from_run_id=...)`. Before restart, inspect
`run_get(detail="full")` on the source run for `launch_spec`, `nextflow_session_uuid`,
`resume_compatible`, and
structured compatibility details. Do not use direct Nextflow resume flags as public inputs.
