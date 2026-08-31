from pathlib import Path

from multimodal_inference.inference.vllm_executor import (
    VLLMInferenceExecutor,
)


def main() -> None:
    image_path = Path(
        "tests/assets/sample.jpg"
    )

    executor = VLLMInferenceExecutor()

    result = executor.generate(
        prompt="Describe this image in one sentence.",
        image_bytes=image_path.read_bytes(),
        content_type="image/jpeg",
    )

    print(
        f"model: {result.model_version}"
    )

    print(
        f"runtime: {result.runtime_version}"
    )

    print(
        f"result: {result.text}"
    )

    print(
        "vLLM multimodal check: PASS"
    )


if __name__ == "__main__":
    main()
