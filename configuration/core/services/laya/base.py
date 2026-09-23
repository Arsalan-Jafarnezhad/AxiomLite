"""Base classes for Laya AI services."""

from abc import ABC
from typing import Any

from .loader import agent


class LayaService(ABC):
    """Base service for structured Laya predictions."""

    schema: dict[str, Any] = {}

    def predict(self, body: str) -> dict[str, Any]:
        """
        Analyze a message using the shared Laya agent.

        Args:
            body: Text to analyze.

        Returns:
            Structured Laya prediction result.

        Raises:
            ValueError: If the service has no schema.
        """
        if not self.schema:
            raise ValueError(f"{self.__class__.__name__} must define a schema.")

        return agent.predict(
            {"body": body},
            self.schema,
        )
