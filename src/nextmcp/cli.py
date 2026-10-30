"""CLI entry point for nextmcp."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

import uvicorn

from nextmcp.config import ConfigValidationError, load_config, redacted_config_dict
from nextmcp.runtime_state import RuntimeState
from nextmcp.server import create_app, create_mcp


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="nextmcp server")
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to config YAML (default: config.yaml or NEXTMCP_CONFIG env)",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate config and exit without starting the server",
    )
    parser.add_argument(
        "--dump-config",
        action="store_true",
        help="Print the effective config with secrets redacted and exit",
    )
    parser.add_argument("--host", default=None, help="Override server host")
    parser.add_argument("--port", type=int, default=None, help="Override server port")
    args = parser.parse_args(argv)

    config_path = args.config or os.environ.get("NEXTMCP_CONFIG", "config.yaml")
    try:
        cfg = load_config(args.config)
        runtime = RuntimeState(cfg, config_path=config_path)
    except ConfigValidationError as exc:
        parser.error(str(exc))

    if args.host is not None:
        cfg.server.host = args.host
    if args.port is not None:
        cfg.server.port = args.port

    if args.check_config:
        print(f"Config OK: {config_path}", file=sys.stdout)
        return

    if args.dump_config:
        print(json.dumps(redacted_config_dict(cfg), indent=2, sort_keys=True), file=sys.stdout)
        return

    host = args.host or cfg.server.host
    port = args.port or cfg.server.port

    logging.basicConfig(
        level=getattr(logging, cfg.server.logging_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    mcp = create_mcp(cfg)

    # Register tools — import here to avoid circular deps
    from nextmcp.tools.capability_tools import register_capability_tools
    from nextmcp.tools.fs_tools import register_fs_tools
    from nextmcp.tools.nextflow_tools import register_nextflow_tools
    from nextmcp.tools.project_tools import register_project_tools
    from nextmcp.tools.run_tools import register_run_tools

    register_capability_tools(mcp, runtime)
    register_fs_tools(mcp, runtime)
    register_project_tools(mcp, runtime)
    register_run_tools(mcp, runtime)
    register_nextflow_tools(mcp, runtime)

    app = create_app(runtime, mcp)

    logging.getLogger(__name__).info("Starting nextmcp on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
