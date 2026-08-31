import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env",
)

OBJECT_STORE_ENDPOINT_URL = os.getenv(
    "OBJECT_STORE_ENDPOINT_URL",
)

OBJECT_STORE_BUCKET = os.environ[
    "OBJECT_STORE_BUCKET"
]

OBJECT_STORE_REGION = os.getenv(
    "OBJECT_STORE_REGION",
    "us-east-1",
)

OBJECT_STORE_MAX_UPLOAD_BYTES = int(
    os.getenv(
        "OBJECT_STORE_MAX_UPLOAD_BYTES",
        "10485760",
    )
)

OBJECT_STORE_PRESIGN_TTL_SECONDS = int(
    os.getenv(
        "OBJECT_STORE_PRESIGN_TTL_SECONDS",
        "300",
    )
)

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

REDIS_STREAM_KEY = os.getenv(
    "REDIS_STREAM_KEY",
    "inference.jobs",
)

REDIS_CONSUMER_GROUP = os.getenv(
    "REDIS_CONSUMER_GROUP",
    "inference-workers",
)

OUTBOX_BATCH_SIZE = int(
    os.getenv(
        "OUTBOX_BATCH_SIZE",
        "25",
    )
)

OUTBOX_CLAIM_SECONDS = int(
    os.getenv(
        "OUTBOX_CLAIM_SECONDS",
        "30",
    )
)

DISPATCHER_POLL_SECONDS = float(
    os.getenv(
        "DISPATCHER_POLL_SECONDS",
        "1",
    )
)

VLLM_BASE_URL = os.getenv(
    "VLLM_BASE_URL",
    "http://127.0.0.1:8001",
)

VLLM_API_KEY = os.environ[
    "VLLM_API_KEY"
]

INFERENCE_MODEL_ID = os.getenv(
    "INFERENCE_MODEL_ID",
    "Qwen/Qwen2.5-VL-7B-Instruct",
)

INFERENCE_MODEL_REVISION = os.getenv(
    "INFERENCE_MODEL_REVISION",
    "cc594898137f460bfe9f0759e9844b3ce807cfb5",
)

INFERENCE_SERVED_MODEL = os.getenv(
    "INFERENCE_SERVED_MODEL",
    "qwen2.5-vl-7b",
)

INFERENCE_MAX_COMPLETION_TOKENS = int(
    os.getenv(
        "INFERENCE_MAX_COMPLETION_TOKENS",
        "256",
    )
)

INFERENCE_TIMEOUT_SECONDS = float(
    os.getenv(
        "INFERENCE_TIMEOUT_SECONDS",
        "120",
    )
)
