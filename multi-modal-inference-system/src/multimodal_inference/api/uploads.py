from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from multimodal_inference import settings
from multimodal_inference.api.dependencies import (
    get_object_store,
)
from multimodal_inference.api.schemas import (
    UploadAuthorizationRequest,
    UploadAuthorizationResponse,
)
from multimodal_inference.storage.object_store import (
    S3ObjectStore,
)


router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
)


@router.post(
    "/authorize",
    response_model=UploadAuthorizationResponse,
)
def authorize_upload(
    request: UploadAuthorizationRequest,
    store: S3ObjectStore = Depends(
        get_object_store
    ),
) -> UploadAuthorizationResponse:

    if (
        request.content_type
        not in settings.ALLOWED_IMAGE_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="unsupported image content type",
        )

    ticket = store.create_upload_ticket(
        request.content_type
    )

    return UploadAuthorizationResponse(
        object_key=ticket.object_key,
        upload_url=ticket.url,
        fields=ticket.fields,
        expires_in=(
            settings.OBJECT_STORE_PRESIGN_TTL_SECONDS
        ),
    )
