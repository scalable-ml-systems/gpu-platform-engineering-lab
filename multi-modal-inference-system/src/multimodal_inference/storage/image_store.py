from pathlib import Path
from typing import Protocol


class ImageStore(Protocol):
    def save(
        self,
        data: bytes,
        suffix: str,
    ) -> str:
        """Persist image bytes and return an image URI."""

    def read(self, image_uri: str) -> bytes:
        """Read image bytes from a stored image URI."""

    def delete(self, image_uri: str) -> None:
        """Delete a stored image."""
