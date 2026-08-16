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
