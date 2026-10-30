"""FastMCP server with bearer token authentication."""

from __future__ import annotations

import logging

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount
from starlette.types import ASGIApp

from nextmcp.audit import AuditMiddleware
from nextmcp.config import AppConfig
from nextmcp.runtime_state import RuntimeState
from nextmcp.tool_response import error_payload

logger = logging.getLogger(__name__)


class ConfigReloadMiddleware(BaseHTTPMiddleware):
    """Refresh runtime config before serving a request when enabled."""

    def __init__(self, app: ASGIApp, runtime: RuntimeState) -> None:
        super().__init__(app)
        self._runtime = runtime

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        self._runtime.maybe_reload()
        return await call_next(request)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Reject requests without a valid static bearer token."""

    def __init__(self, app: ASGIApp, runtime: RuntimeState) -> None:
        super().__init__(app)
        self._runtime = runtime

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        self._runtime.maybe_reload()
        auth_cfg = self._runtime.cfg.auth
        if not auth_cfg.enabled or not auth_cfg.bearer_token:
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != auth_cfg.bearer_token:
            return JSONResponse(
                error_payload(
                    error_code="unauthorized",
                    message="Bearer token is missing or invalid",
                    suggestions=(
                        "Send Authorization: Bearer <token>.",
                        "Check auth.enabled and auth.bearer_token in config.yaml.",
                    ),
                ),
                status_code=401,
            )
        return await call_next(request)


def create_mcp(cfg: AppConfig) -> FastMCP:
    """Create the FastMCP server instance (tools registered elsewhere)."""
    return FastMCP(name="nextmcp")


def create_app(runtime: RuntimeState, mcp: FastMCP) -> Starlette:
    """Build the full ASGI app: FastMCP mounted at /mcp with optional auth."""
    mcp_app = mcp.http_app(path="/mcp")
    cfg = runtime.cfg

    middlewares: list[Middleware] = [
        Middleware(ConfigReloadMiddleware, runtime=runtime),
        Middleware(AuditMiddleware),
        Middleware(BearerAuthMiddleware, runtime=runtime),
    ]
    if cfg.auth.enabled and cfg.auth.bearer_token:
        logger.info("Bearer token auth enabled")
    else:
        logger.warning("Auth disabled — server is open to all requests")

    app = Starlette(
        routes=[Mount("/", app=mcp_app)],
        middleware=middlewares,
        lifespan=mcp_app.lifespan,
    )
    return app
