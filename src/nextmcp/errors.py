"""Shared exception types for stable agent-facing error mapping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceNotFoundError(Exception):
    """Raised when a named domain resource does not exist."""

    resource_type: str
    resource_id: str
    message: str | None = None

    def __str__(self) -> str:
        """Return a stable human-readable error message."""
        if self.message is not None:
            return self.message
        return f"Unknown {self.resource_type}: {self.resource_id}"
