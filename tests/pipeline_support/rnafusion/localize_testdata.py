#!/usr/bin/env python3
"""Localize nf-core/rnafusion test-build inputs into nextmcp server paths."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from urllib.parse import urlparse
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SAMPLESHEET = REPO_ROOT / "nf_pipeline" / "rnafusion" / "tests" / "csv" / "fastq.csv"

LOCALIZED_ROOT = Path("/data/nextmcp/testdata/rnafusion/test_build")
PROJECT_FILES_ROOT = LOCALIZED_ROOT / "project-files" / "pipeline-support-rnafusion"
FUSIONREPORT_DB_ROOT = LOCALIZED_ROOT / "inputs" / "fusion_report_db"

PREFIX_MAPPINGS: tuple[tuple[str, Path], ...] = (
    ("https://raw.githubusercontent.com/nf-core/test-datasets/", Path("pipeline-data")),
    ("https://github.com/nf-core/test-datasets/raw/", Path("pipeline-data")),
)

DIRECT_URLS = (
    "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.fa",
    "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.gtf",
    "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/CTAT_HumanFusionLib.mini.dat.gz",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3f",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3i",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3m",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3p",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/human/Pfam-A.hmm.gz",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/reference/arriba/protein_domains_hg38_GRCh38_v2.5.0.gff3",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/reference/arriba/known_fusions_hg38_GRCh38_v2.5.0.tsv.gz",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/reference/arriba/blacklist_hg38_GRCh38_v2.5.0.tsv.gz",
    "https://github.com/nf-core/test-datasets/raw/refs/heads/rnafusion/testdata/reference/arriba/cytobands_hg38_GRCh38_v2.5.0.tsv",
)

REQUIRED_FUSIONREPORT_FILES = (
    "fusiongdb2.db",
    "mitelman.db",
    "DB-timestamp.txt",
)

OVERRIDE_CONTENT = dedent(
    """\
    params {
        genomes_base = "${params.outdir}/references"
    }

    process {
        resourceLimits = [
            cpus: 4,
            memory: '15.GB',
            time: '1.h'
        ]

        withName: 'STARFUSION_BUILD' {
            ext.args = ''
        }
    }
    """
)


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def _is_remote_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _local_path_for_url(localized_root: Path, url: str) -> Path:
    for remote_prefix, local_suffix in PREFIX_MAPPINGS:
        if url.startswith(remote_prefix):
            return localized_root / local_suffix / url.removeprefix(remote_prefix)

    parsed = urlparse(url)
    return localized_root / "downloads" / parsed.netloc / parsed.path.lstrip("/")


def _copy_local_file(source_path: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        _log(f"Reusing existing copied file {destination}")
        return

    _log(f"Copying {source_path} -> {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)


def _rewrite_path_for_manifest(localized_root: Path, source_path: Path) -> Path:
    relative_path = source_path.relative_to(localized_root)
    return (
        localized_root
        / "rewrites"
        / relative_path.parent
        / f"{source_path.stem}_local{source_path.suffix}"
    )


def _download(url: str, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        _log(f"Reusing existing file {destination}")
        return

    _log(f"Downloading {url} -> {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url) as response:
        destination.write_bytes(response.read())


def _rewrite_cell(value: str, localized_root: Path, force: bool) -> str:
    parts = value.split(";")
    rewritten: list[str] = []
    for part in parts:
        item = part.strip()
        if _is_remote_url(item):
            local_path = _local_path_for_url(localized_root, item)
            _download(item, local_path, force)
            rewritten.append(str(local_path))
        else:
            rewritten.append(part)
    return ";".join(rewritten)


def _rewrite_csv_manifest(localized_root: Path, source_path: Path, force: bool) -> Path:
    rewritten_path = _rewrite_path_for_manifest(localized_root, source_path)
    _log(f"Rewriting local CSV manifest {rewritten_path}")

    with source_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    rewritten_rows: list[dict[str, str]] = []
    for row in rows:
        rewritten_row = dict(row)
        for key, value in row.items():
            if value is None:
                continue
            rewritten_row[key] = _rewrite_cell(value, localized_root, force)
        rewritten_rows.append(rewritten_row)

    rewritten_path.parent.mkdir(parents=True, exist_ok=True)
    with rewritten_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rewritten_rows)

    return rewritten_path


def _write_override_config(project_files_root: Path) -> Path:
    override_path = project_files_root / "profile_test_build_overrides.config"
    _log(f"Writing override config to {override_path}")
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text(OVERRIDE_CONTENT, encoding="utf-8")
    return override_path


def _has_required_fusionreport_files(path: Path) -> bool:
    return all((path / name).exists() for name in REQUIRED_FUSIONREPORT_FILES)


def _copy_tree(source_root: Path, destination_root: Path, force: bool) -> None:
    for source_path in source_root.rglob("*"):
        relative_path = source_path.relative_to(source_root)
        destination = destination_root / relative_path
        if source_path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists() and not force:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)


def _ensure_fusionreport_db(
    destination_root: Path,
    *,
    source_root: Path | None,
    force: bool,
) -> Path:
    if _has_required_fusionreport_files(destination_root) and not force:
        _log(f"Reusing existing FusionReport database {destination_root}")
        return destination_root

    if source_root is not None:
        if not _has_required_fusionreport_files(source_root):
            raise RuntimeError(
                "The provided --fusionreport-db path does not contain "
                "fusiongdb2.db, mitelman.db, and DB-timestamp.txt."
            )
        _log(f"Copying prebuilt FusionReport database {source_root} -> {destination_root}")
        _copy_tree(source_root, destination_root, force=True)
        return destination_root

    executable = shutil.which("fusion_report")
    if executable is None:
        raise RuntimeError(
            "FusionReport localization requires either --fusionreport-db "
            "or a host-side `fusion_report` executable."
        )

    _log("Building FusionReport database with `fusion_report download --no-cosmic`")
    download_root = destination_root.parent / "_fusionreport_download"
    if download_root.exists() and force:
        shutil.rmtree(download_root)
    download_root.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [executable, "download", "--no-cosmic", "./"],
        cwd=download_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    destination_root.mkdir(parents=True, exist_ok=True)
    for path in download_root.iterdir():
        if path.suffix not in {".db", ".txt", ".log"}:
            continue
        shutil.move(str(path), destination_root / path.name)

    if not _has_required_fusionreport_files(destination_root):
        raise RuntimeError(
            "FusionReport download completed but the expected database files were not created."
        )

    return destination_root


def localize(
    localized_root: Path,
    project_files_root: Path,
    *,
    fusionreport_db: Path | None,
    force: bool = False,
) -> dict[str, str]:
    _log(f"Starting localization under {localized_root}")

    copied_samplesheet = localized_root / "repo-assets" / "tests" / "csv" / "fastq.csv"
    _copy_local_file(SOURCE_SAMPLESHEET, copied_samplesheet, force)
    rewritten_samplesheet = _rewrite_csv_manifest(localized_root, copied_samplesheet, force)

    downloaded_paths: dict[str, Path] = {}
    for url in DIRECT_URLS:
        local_path = _local_path_for_url(localized_root, url)
        _download(url, local_path, force)
        downloaded_paths[url] = local_path

    fusionreport_root = _ensure_fusionreport_db(
        FUSIONREPORT_DB_ROOT,
        source_root=fusionreport_db,
        force=force,
    )
    override_path = _write_override_config(project_files_root)

    _log("Localization complete")
    return {
        "samplesheet": str(rewritten_samplesheet),
        "copied_samplesheet": str(copied_samplesheet),
        "fastq_root": str(
            localized_root
            / "pipeline-data"
            / "81cb45949e75cbb85cbf6c5ec9009ab45b160823"
            / "testdata"
            / "human"
        ),
        "minigenome_fasta": str(
            downloaded_paths[
                "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.fa"
            ]
        ),
        "minigenome_gtf": str(
            downloaded_paths[
                "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.gtf"
            ]
        ),
        "fusion_annot_lib": str(
            downloaded_paths[
                "https://github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/CTAT_HumanFusionLib.mini.dat.gz"
            ]
        ),
        "fusionreport_ref": str(fusionreport_root),
        "override_config": str(override_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy and localize the nf-core/rnafusion test-build inputs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=LOCALIZED_ROOT,
        help="Server-local root where the localized test bundle will be written.",
    )
    parser.add_argument(
        "--case-root",
        type=Path,
        default=PROJECT_FILES_ROOT,
        help="Server-local project-files root where the override config will be written.",
    )
    parser.add_argument(
        "--fusionreport-db",
        type=Path,
        default=None,
        help="Optional prebuilt FusionReport database directory to copy into the localized bundle.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-copy or re-download files even when localized copies already exist.",
    )
    args = parser.parse_args()

    try:
        payload = localize(
            args.root,
            args.case_root,
            fusionreport_db=args.fusionreport_db,
            force=args.force,
        )
    except Exception as exc:  # pragma: no cover - surfaced to calling shell
        _log(f"Localization failed: {exc}")
        print(
            json.dumps(
                {
                    "ok": False,
                    "localized_root": str(args.root),
                    "blocker": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    print(json.dumps({"ok": True, **payload}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
