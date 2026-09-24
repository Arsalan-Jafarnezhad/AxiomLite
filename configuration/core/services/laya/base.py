"""Base classes for Laya AI services."""

from abc import ABC
from typing import Any

from httpx import post
from django.conf import settings


class LayaService(ABC):
    """Base service for httpx to the shared Laya server."""

    schema: dict[str, Any] = {}

    def predict(self, body: str) -> dict[str, Any]:
        """
        Analyze text using the shared Laya server.

        Args:
            body: Text to analyze.

        Returns:
            Structured Laya prediction result.

        Raises:
            ValueError: If no schema is defined.
            httpx.RequestException: If Laya cannot be reached.
        """
        if not self.schema:
            raise ValueError(f"{self.__class__.__name__} must define a schema.")

        laya_url = getattr(
            settings,
            "LAYA_URL",
            "http://localhost:8000",
        )

        response = post(
            f"{laya_url.rstrip('/')}/v1/systemone",
            json={
                "state": {
                    "body": body,
                },
                "questions": self.schema,
            },
            timeout=60,
        )

        response.raise_for_status()

        return response.json()
