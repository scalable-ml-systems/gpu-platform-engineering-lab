import uuid
from dataclasses import dataclass

import boto3
from botocore.config import Config

from multimodal_inference import settings


@dataclass(frozen=True)
class UploadTicket:
    object_key: str
    url: str
    fields: dict[str, str]


class S3ObjectStore:
    def __init__(self) -> None:
        self.bucket = settings.OBJECT_STORE_BUCKET

        self.client = boto3.client(
            "s3",
            region_name=settings.OBJECT_STORE_REGION,
            endpoint_url=settings.OBJECT_STORE_ENDPOINT_URL,
            config=Config(
                signature_version="s3v4",
            ),
        )

    def create_upload_ticket(
        self,
        content_type: str,
    ) -> UploadTicket:
        if not content_type.startswith("image/"):
            raise ValueError(
                "content type must be image/*"
            )

        object_key = f"inputs/{uuid.uuid4()}"

        response = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=object_key,
            Fields={
                "Content-Type": content_type,
            },
            Conditions=[
                {
                    "Content-Type": content_type,
                },
                [
                    "content-length-range",
                    1,
                    settings.OBJECT_STORE_MAX_UPLOAD_BYTES,
                ],
            ],
            ExpiresIn=(
                settings.OBJECT_STORE_PRESIGN_TTL_SECONDS
            ),
        )

        return UploadTicket(
            object_key=object_key,
            url=response["url"],
            fields=response["fields"],
        )

    def head(
        self,
        object_key: str,
    ) -> dict:
        return self.client.head_object(
            Bucket=self.bucket,
            Key=object_key,
        )

    def create_download_url(
        self,
        object_key: str,
        expires_in: int = 300,
    ) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )

    def delete(
        self,
        object_key: str,
    ) -> None:
        self.client.delete_object(
            Bucket=self.bucket,
            Key=object_key,
        )
