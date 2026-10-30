#!/usr/bin/env python3
"""Validate the local rnaseq smoke cache and write the launch override config."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

LOCALIZED_ROOT = Path("/data/rnaseq_test_data")
PROJECT_FILES_ROOT = LOCALIZED_ROOT / "project-files" / "pipeline-support-rnaseq"
OVERRIDE_PATH = PROJECT_FILES_ROOT / "profile_test_overrides.config"

REQUIRED_FILES = [
    LOCALIZED_ROOT / "samplesheet_test_local.csv",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/genome.fasta",
    LOCALIZED_ROOT
    / "626c8fab639062eade4b10747e919341cbf9b41a/reference/genes_with_empty_tid.gtf.gz",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/genes.gff.gz",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/transcriptome.fasta",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/gfp.fa.gz",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/bbsplit_fasta_list.txt",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/hisat2.tar.gz",
    LOCALIZED_ROOT / "626c8fab639062eade4b10747e919341cbf9b41a/reference/salmon.tar.gz",
]

OVERRIDE_CONTENT = dedent(
    """\
    process {
        resourceLimits = [
            cpus  : 4,
            memory: '15.GB',
            time  : '1.h'
        ]
    }

    process {
        withName: 'RSEM_PREPAREREFERENCE_GENOME|SENTIEON_RSEMPREPAREREFERENCE_GENOME' {
            ext.args2 = "--genomeSAindexNbases 7"
        }
    }
    """
)


def log(message: str) -> None:
    """Write concise progress lines to stderr."""
    print(message, file=sys.stderr)


def main() -> int:
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]

    if missing:
        for path in missing:
            log(f"missing local cache path: {path}")
        print(
            json.dumps(
                {
                    "ok": False,
                    "localized_root": str(LOCALIZED_ROOT),
                    "missing_paths": missing,
                },
                indent=2,
            )
        )
        return 1

    PROJECT_FILES_ROOT.mkdir(parents=True, exist_ok=True)
    OVERRIDE_PATH.write_text(OVERRIDE_CONTENT, encoding="utf-8")

    log(f"validated local cache under {LOCALIZED_ROOT}")
    log(f"wrote config override file to {OVERRIDE_PATH}")

    print(
        json.dumps(
            {
                "ok": True,
                "localized_root": str(LOCALIZED_ROOT),
                "config_override_file": str(OVERRIDE_PATH),
                "required_paths": [str(path) for path in REQUIRED_FILES],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
