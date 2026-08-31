import base64

import httpx

from multimodal_inference import settings
from multimodal_inference.worker.executor import (
    InferenceResult,
)


class VLLMInferenceExecutor:
    def __init__(self) -> None:
        self.client = httpx.Client(
            base_url=settings.VLLM_BASE_URL,
            headers={
                "Authorization":
                    f"Bearer {settings.VLLM_API_KEY}"
            },
            timeout=settings.INFERENCE_TIMEOUT_SECONDS,
        )

        self.runtime_version = (
            self._read_runtime_version()
        )

    def _read_runtime_version(self) -> str:
        response = self.client.get(
            "/version"
        )

        response.raise_for_status()

        payload = response.json()

        return str(payload["version"])

    def generate(
        self,
        *,
        prompt: str,
        image_bytes: bytes,
        content_type: str,
    ) -> InferenceResult:

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("ascii")

        image_data_url = (
            f"data:{content_type};base64,"
            f"{encoded_image}"
        )

        response = self.client.post(
            "/v1/chat/completions",
            json={
                "model":
                    settings.INFERENCE_SERVED_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url":
                                        image_data_url
                                },
                            },
                        ],
                    }
                ],
                "temperature": 0,
                "max_completion_tokens": (
                    settings
                    .INFERENCE_MAX_COMPLETION_TOKENS
                ),
            },
        )

        response.raise_for_status()

        payload = response.json()

        choices = payload.get(
            "choices",
            [],
        )

        if not choices:
            raise RuntimeError(
                "vLLM returned no completion"
            )

        text = (
            choices[0]
            ["message"]
            ["content"]
        )

        if not isinstance(text, str) or not text.strip():
            raise RuntimeError(
                "vLLM returned empty completion"
            )

        model_version = (
            f"{settings.INFERENCE_MODEL_ID}"
            f"@{settings.INFERENCE_MODEL_REVISION}"
        )

        runtime_version = (
            f"vllm-{self.runtime_version}"
        )

        return InferenceResult(
            text=text,
            model_version=model_version,
            runtime_version=runtime_version,
        )
