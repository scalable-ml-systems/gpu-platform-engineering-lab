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
