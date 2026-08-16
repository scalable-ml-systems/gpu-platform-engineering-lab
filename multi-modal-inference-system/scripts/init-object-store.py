from botocore.exceptions import ClientError

from multimodal_inference import settings
from multimodal_inference.storage.object_store import (
    S3ObjectStore,
)


def main() -> None:
    store = S3ObjectStore()

    try:
        store.client.head_bucket(
            Bucket=settings.OBJECT_STORE_BUCKET
        )

        print(
            f"bucket exists: "
            f"{settings.OBJECT_STORE_BUCKET}"
        )

        return

    except ClientError:
        pass

    if settings.OBJECT_STORE_REGION == "us-east-1":
        store.client.create_bucket(
            Bucket=settings.OBJECT_STORE_BUCKET
        )
    else:
        store.client.create_bucket(
            Bucket=settings.OBJECT_STORE_BUCKET,
            CreateBucketConfiguration={
                "LocationConstraint":
                    settings.OBJECT_STORE_REGION
            },
        )

    print(
        f"bucket created: "
        f"{settings.OBJECT_STORE_BUCKET}"
    )


if __name__ == "__main__":
    main()
