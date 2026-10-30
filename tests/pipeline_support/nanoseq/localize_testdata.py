"""Download and localize nf-core/nanoseq smoke-test inputs into server paths."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

LOCALIZED_ROOT = Path("/data/nextmcp/testdata/nanoseq/test")
PROJECT_FILES_ROOT = LOCALIZED_ROOT / "project-files" / "pipeline-support-nanoseq"

PREFIX_MAPPINGS: tuple[tuple[str, Path], ...] = (
    ("https://raw.githubusercontent.com/nf-core/test-datasets/", Path("pipeline-data")),
    ("https://github.com/nf-core/test-datasets/raw/", Path("pipeline-data")),
)

SAMPLESHEET_URL = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/"
    "nanoseq/3.0/samplesheet/samplesheet_nobc_dx.csv"
)
INPUT_FASTQ_URL = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/"
    "nanoseq/fastq/nondemultiplexed/sample_nobc_dx.fastq.gz"
)

DIRECT_URLS = (
    SAMPLESHEET_URL,
    INPUT_FASTQ_URL,
)

OVERRIDE_CONTENT = """params.max_cpus = 2
params.max_memory = '6.GB'
params.max_time = '12.h'
"""


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
    override_path = project_files_root / "max_resources.config"
    _log(f"Writing override config to {override_path}")
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text(OVERRIDE_CONTENT, encoding="utf-8")
    return override_path


def localize(localized_root: Path, project_files_root: Path, force: bool = False) -> dict[str, str]:
    _log(f"Starting localization under {localized_root}")

    downloaded_paths: dict[str, Path] = {}
    for url in DIRECT_URLS:
        local_path = _local_path_for_url(localized_root, url)
        _download(url, local_path, force)
        downloaded_paths[url] = local_path

    rewritten_samplesheet = _rewrite_csv_manifest(
        localized_root,
        downloaded_paths[SAMPLESHEET_URL],
        force,
    )
    reference_fasta = _local_path_for_url(
        localized_root,
        "https://raw.githubusercontent.com/nf-core/test-datasets/nanoseq/reference/hg19_KCMF1.fa",
    )
    override_path = _write_override_config(project_files_root)

    _log("Localization complete")
    return {
        "input_fastq": str(downloaded_paths[INPUT_FASTQ_URL]),
        "override_config": str(override_path),
        "reference_fasta": str(reference_fasta),
        "samplesheet": str(rewritten_samplesheet),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and localize the nf-core/nanoseq smoke-test inputs."
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
        "--force",
        action="store_true",
        help="Re-download files even when the localized copies already exist.",
    )
    args = parser.parse_args()

    payload = localize(args.root, args.case_root, force=args.force)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
