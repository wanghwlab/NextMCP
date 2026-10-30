"""Localize nf-core/atacseq test inputs into nextmcp server paths."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

LOCALIZED_ROOT = Path("/data/nextmcp/testdata/atacseq/test")
PREFIX_MAPPINGS: tuple[tuple[str, Path], ...] = (
    ("https://raw.githubusercontent.com/nf-core/test-datasets/atacseq/", Path("pipeline-data")),
)

SAMPLESHEET_URL = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/atacseq/"
    "samplesheet/v2.0/samplesheet_test.csv"
)
DIRECT_URLS = (
    "https://raw.githubusercontent.com/nf-core/test-datasets/atacseq/reference/genome.fa",
    "https://raw.githubusercontent.com/nf-core/test-datasets/atacseq/reference/genes.gtf",
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


def localize(localized_root: Path, force: bool = False) -> Path:
    _log(f"Starting localization under {localized_root}")
    samplesheet_path = _local_path_for_url(localized_root, SAMPLESHEET_URL)
    _download(SAMPLESHEET_URL, samplesheet_path, force)

    for url in DIRECT_URLS:
        _download(url, _local_path_for_url(localized_root, url), force)

    rewritten_path = _rewrite_path_for_manifest(localized_root, samplesheet_path)
    _log(f"Rewriting local manifest {rewritten_path}")
    with samplesheet_path.open("r", encoding="utf-8", newline="") as handle:
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

    _log(f"Localization complete: {rewritten_path}")
    return rewritten_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and localize the nf-core/atacseq smoke-test inputs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=LOCALIZED_ROOT,
        help="Server-local root where the localized test bundle will be written.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even when the localized copies already exist.",
    )
    args = parser.parse_args()

    rewritten_path = localize(args.root, force=args.force)
    print(rewritten_path)


if __name__ == "__main__":
    main()
