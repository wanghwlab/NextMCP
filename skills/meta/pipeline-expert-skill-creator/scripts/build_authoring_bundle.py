"""Build an inspect-equivalent authoring bundle from a repository-local pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nextmcp.nextflow_catalog import build_pipeline_inspect_payload, load_local_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a nextflow_inspect_pipeline(detail='materials') equivalent bundle."
    )
    parser.add_argument(
        "--pipeline",
        required=True,
        help="Path to a repository-local pipeline directory such as nf_pipeline/rnaseq.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output path. Prints to stdout when omitted.",
    )
    args = parser.parse_args()

    pipeline_path = Path(args.pipeline).resolve()
    record = load_local_pipeline(pipeline_path)
    payload = build_pipeline_inspect_payload(record, detail="materials")
    rendered = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
