import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

from .image_store import ImageStore


class LocalImageStore(ImageStore):
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        data: bytes,
        suffix: str,
    ) -> str:
        if not data:
            raise ValueError("image data is empty")

        suffix = suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise ValueError(f"unsupported image suffix: {suffix}")

        image_id = uuid.uuid4()
        destination = self.root / f"{image_id}{suffix}"
        temporary = self.root / f".{image_id}.tmp"

        temporary.write_bytes(data)
        os.replace(temporary, destination)

        return destination.as_uri()

    def read(self, image_uri: str) -> bytes:
        path = self._resolve_uri(image_uri)

        if not path.is_file():
            raise FileNotFoundError(image_uri)

        return path.read_bytes()

    def delete(self, image_uri: str) -> None:
        path = self._resolve_uri(image_uri)
        path.unlink(missing_ok=True)

    def _resolve_uri(self, image_uri: str) -> Path:
        parsed = urlparse(image_uri)

        if parsed.scheme != "file":
            raise ValueError(f"unsupported image URI: {image_uri}")

        path = Path(parsed.path).resolve()

        if not path.is_relative_to(self.root):
            raise ValueError(
                "image URI is outside configured storage root"
            )

        return path
