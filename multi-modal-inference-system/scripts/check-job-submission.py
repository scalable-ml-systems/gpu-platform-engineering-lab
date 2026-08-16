import os
import uuid
from pathlib import Path

import psycopg
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / ".env",
)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000",
)

DATABASE_URL = os.environ[
    "DATABASE_URL"
]

SOURCE_IMAGE = PROJECT_ROOT / "tests/assets/sample.jpg"

CONTENT_TYPE = "image/jpeg"
INITIAL_PROMPT = "Describe this image."
CHANGED_PROMPT = "Is this even an image."


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(
            message,
        )


def authorize_upload() -> dict:
    response = requests.post(
        f"{API_BASE_URL}/uploads/authorize",
        json={
            "content_type": CONTENT_TYPE,
        },
        timeout=30,
    )

    require(
        response.status_code == 201,
        (
            "upload authorization failed: "
            f"{response.status_code} "
            f"{response.text}"
        ),
    )

    payload = response.json()

    require(
        "object_key" in payload,
        "authorization response missing object_key",
    )

    require(
        "upload_url" in payload,
        "authorization response missing upload_url",
    )

    require(
        "fields" in payload,
        "authorization response missing fields",
    )

    return payload


def upload_image(
    ticket: dict,
) -> None:
    require(
        SOURCE_IMAGE.is_file(),
        f"sample image not found: {SOURCE_IMAGE}",
    )

    with SOURCE_IMAGE.open("rb") as source:
        response = requests.post(
            ticket["upload_url"],
            data=ticket["fields"],
            files={
                "file": (
                    SOURCE_IMAGE.name,
                    source,
                    CONTENT_TYPE,
                ),
            },
            timeout=30,
        )

    require(
        response.status_code == 204,
        (
            "direct object-store upload failed: "
            f"{response.status_code} "
            f"{response.text}"
        ),
    )


def create_job(
    object_key: str,
    idempotency_key: str,
    prompt: str,
) -> requests.Response:
    return requests.post(
        f"{API_BASE_URL}/jobs",
        headers={
            "Idempotency-Key": idempotency_key,
        },
        json={
            "object_key": object_key,
            "prompt": prompt,
        },
        timeout=30,
    )


def count_jobs(
    idempotency_key: str,
) -> int:
    with psycopg.connect(
        DATABASE_URL,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM jobs
                WHERE idempotency_key = %s
                """,
                (idempotency_key,),
            )

            row = cursor.fetchone()

    require(
        row is not None,
        "Postgres count query returned no row",
    )

    return row[0]


def main() -> None:
    idempotency_key = (
        f"check-job-submission-{uuid.uuid4()}"
    )

    print("1. Requesting upload authorization...")

    ticket = authorize_upload()

    object_key = ticket["object_key"]

    print(
        f"   Authorized key: {object_key}"
    )

    print("2. Uploading image directly to MinIO...")

    upload_image(
        ticket,
    )

    print("   Direct upload: PASS")

    print("3. Creating Job...")

    first_response = create_job(
        object_key=object_key,
        idempotency_key=idempotency_key,
        prompt=INITIAL_PROMPT,
    )

    require(
        first_response.status_code == 201,
        (
            "first job creation failed: "
            f"{first_response.status_code} "
            f"{first_response.text}"
        ),
    )

    first_job = first_response.json()

    require(
        first_job["state"] == "VALIDATED",
        (
            "new job was not VALIDATED: "
            f"{first_job}"
        ),
    )

    job_id = first_job["job_id"]

    print(
        f"   Created Job: {job_id}"
    )

    print("4. Repeating identical request...")

    replay_response = create_job(
        object_key=object_key,
        idempotency_key=idempotency_key,
        prompt=INITIAL_PROMPT,
    )

    require(
        replay_response.status_code == 200,
        (
            "idempotent replay did not return 200: "
            f"{replay_response.status_code} "
            f"{replay_response.text}"
        ),
    )

    replay_job = replay_response.json()

    require(
        replay_job["job_id"] == job_id,
        (
            "idempotent replay returned "
            "a different job_id"
        ),
    )

    print(
        "   Idempotent replay: PASS"
    )

    print(
        "5. Reusing key with a changed prompt..."
    )

    conflict_response = create_job(
        object_key=object_key,
        idempotency_key=idempotency_key,
        prompt=CHANGED_PROMPT,
    )

    require(
        conflict_response.status_code == 409,
        (
            "changed request with same idempotency "
            "key did not return 409: "
            f"{conflict_response.status_code} "
            f"{conflict_response.text}"
        ),
    )

    print(
        "   Idempotency conflict: PASS"
    )

    print("6. Checking Postgres...")

    job_count = count_jobs(
        idempotency_key,
    )

    require(
        job_count == 1,
        (
            "expected exactly one Job for "
            f"idempotency key; found {job_count}"
        ),
    )

    print(
        "   Postgres row count: PASS"
    )

    print(
        "check job submission: PASS"
    )


if __name__ == "__main__":
    main()
