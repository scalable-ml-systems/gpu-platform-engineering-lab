from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InferenceResult:
    text: str
    model_version: str
    runtime_version: str


class InferenceExecutor(Protocol):
    def generate(
        self,
        *,
        prompt: str,
        image_bytes: bytes,
        content_type: str,
    ) -> InferenceResult:
        ...
