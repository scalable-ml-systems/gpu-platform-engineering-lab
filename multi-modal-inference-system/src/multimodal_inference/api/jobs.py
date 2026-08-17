import uuid

from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from multimodal_inference import settings
from multimodal_inference.api.dependencies import (
    get_database,
    get_object_store,
)
from multimodal_inference.api.schemas import (
    JobCreateRequest,
    JobResponse,
)
from multimodal_inference.storage.models import (
    Job,
    JobState,
)
from multimodal_inference.storage.object_store import (
    S3ObjectStore,
)

from multimodal_inference.storage.models import (
    DispatchOutbox,
    Job,
    JobState,
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def validate_object_key(
    object_key: str,
) -> None:
    prefix = "inputs/"

    if not object_key.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid object key",
        )

    object_id = object_key.removeprefix(
        prefix,
    )

    try:
        uuid.UUID(
            object_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid object key",
        ) from exc


def request_matches_job(
    job: Job,
    request: JobCreateRequest,
) -> bool:
    return (
        job.image_object_key
        == request.object_key
        and job.prompt
        == request.prompt
    )


def validate_object_metadata(
    metadata: dict,
) -> tuple[str, int]:
    content_type = metadata.get(
        "ContentType",
    )

    size_bytes = metadata.get(
        "ContentLength",
    )

    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unsupported image content type",
        )

    if not isinstance(size_bytes, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded image size is unavailable",
        )

    if size_bytes <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded image is empty",
        )

    if size_bytes > settings.OBJECT_STORE_MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded image exceeds size limit",
        )

    return content_type, size_bytes


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    request: JobCreateRequest,
    response: Response,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
    database: Session = Depends(
        get_database,
    ),
    store: S3ObjectStore = Depends(
        get_object_store,
    ),
) -> Job:
    validate_object_key(
        request.object_key,
    )

    existing_job = database.scalar(
        select(Job).where(
            Job.idempotency_key
            == idempotency_key
        )
    )

    if existing_job is not None:
        if request_matches_job(
            existing_job,
            request,
        ):
            response.status_code = (
                status.HTTP_200_OK
            )

            return existing_job

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "idempotency key already used "
                "for a different request"
            ),
        )

    try:
        metadata = store.head(
            request.object_key,
        )
    except ClientError as exc:
        error_code = (
            exc.response
            .get("Error", {})
            .get("Code")
        )

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="uploaded image not found",
            ) from exc

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail="object storage unavailable",
        ) from exc

    content_type, size_bytes = (
        validate_object_metadata(
            metadata,
        )
    )

    job = Job(
    idempotency_key=idempotency_key,
    state=JobState.QUEUED,
    prompt=request.prompt,
    image_bucket=store.bucket,
    image_object_key=request.object_key,
    image_content_type=content_type,
    image_size_bytes=size_bytes,
)

database.add(job)

# INSERT the Job inside the current transaction so
# job.job_id exists, but DO NOT commit.
database.flush()

outbox_event = DispatchOutbox(
    job_id=job.job_id,
    event_type="job.ready",
    schema_version=1,
)

database.add(outbox_event)

try:
    database.commit()

except IntegrityError:
    database.rollback()

    existing_job = database.scalar(
        select(Job).where(
            Job.idempotency_key
            == idempotency_key
        )
    )

    if (
        existing_job is not None
        and request_matches_job(
            existing_job,
            request,
        )
    ):
        response.status_code = (
            status.HTTP_200_OK
        )

        return existing_job

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="idempotency key conflict",
    )

database.refresh(job)

response.status_code = status.HTTP_201_CREATED

return job
