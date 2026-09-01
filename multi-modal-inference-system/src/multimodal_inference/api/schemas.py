from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from multimodal_inference.storage.models import JobState


class UploadAuthorizationRequest(BaseModel):
    content_type: str = Field(
        min_length=1,
        max_length=100,
    )


class UploadAuthorizationResponse(BaseModel):
    object_key: str
    upload_url: str
    fields: dict[str, str]
    expires_in: int


class JobCreateRequest(BaseModel):
    object_key: str = Field(
        min_length=1,
        max_length=1024,
    )

    prompt: str = Field(
        min_length=1,
        max_length=16000,
    )

class JobResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    job_id: UUID
    request_id: UUID
    state: JobState

    image_object_key: str

    result: str | None
    failure_reason: str | None

    model_version: str | None
    runtime_version: str | None

    created_at: datetime
    completed_at: datetime | None
