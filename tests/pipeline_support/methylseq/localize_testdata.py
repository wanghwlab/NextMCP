"""Localize nf-core/methylseq test inputs into nextmcp server paths."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SAMPLESHEET = REPO_ROOT / "nf_pipeline" / "methylseq" / "assets" / "samplesheet.csv"

LOCALIZED_ROOT = Path("/data/nextmcp/testdata/methylseq/test")
PROJECT_FILES_ROOT = LOCALIZED_ROOT / "project-files" / "pipeline-support-methylseq"

PREFIX_MAPPINGS: tuple[tuple[str, Path], ...] = (
    ("https://raw.githubusercontent.com/nf-core/test-datasets/", Path("pipeline-data")),
    ("https://github.com/nf-core/test-datasets/raw/", Path("pipeline-data")),
)

FASTA_URL = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/methylseq/reference/genome.fa.gz"
)
FASTFAI_URL = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/methylseq/reference/genome.fa.fai"
)

DIRECT_URLS = (
    FASTA_URL,
    FASTFAI_URL,
)

OVERRIDE_CONTENT = """process {
    resourceLimits = [
        cpus: 4,
        memory: '15.GB',
        time: '1.h'
    ]
}
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


def _copy_local_file(source_path: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        _log(f"Reusing existing copied file {destination}")
        return

    _log(f"Copying {source_path} -> {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source_path.read_bytes())


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
    override_path = project_files_root / "profile_test_overrides.config"
    _log(f"Writing override config to {override_path}")
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text(OVERRIDE_CONTENT, encoding="utf-8")
    return override_path


def localize(localized_root: Path, project_files_root: Path, force: bool = False) -> dict[str, str]:
    _log(f"Starting localization under {localized_root}")

    copied_samplesheet = localized_root / "repo-assets" / "assets" / "samplesheet.csv"
    _copy_local_file(SOURCE_SAMPLESHEET, copied_samplesheet, force)

    downloaded_paths: dict[str, Path] = {}
    for url in DIRECT_URLS:
        local_path = _local_path_for_url(localized_root, url)
        _download(url, local_path, force)
        downloaded_paths[url] = local_path

    rewritten_samplesheet = _rewrite_csv_manifest(localized_root, copied_samplesheet, force)
    override_path = _write_override_config(project_files_root)

    _log("Localization complete")
    return {
        "copied_samplesheet": str(copied_samplesheet),
        "fasta": str(downloaded_paths[FASTA_URL]),
        "fasta_index": str(downloaded_paths[FASTFAI_URL]),
        "fastq_root": str(localized_root / "pipeline-data" / "methylseq" / "testdata"),
        "override_config": str(override_path),
        "samplesheet": str(rewritten_samplesheet),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy and localize the nf-core/methylseq smoke-test inputs."
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
        help="Re-copy or re-download files even when localized copies already exist.",
    )
    args = parser.parse_args()

    payload = localize(args.root, args.case_root, force=args.force)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
