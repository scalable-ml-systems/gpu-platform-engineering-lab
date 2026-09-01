from uuid import uuid4

from multimodal_inference.api.dependencies import (
    get_database,
)
from multimodal_inference.storage.models import (
    Job,
    JobState,
)


def main() -> None:
    database = next(get_database())

    try:
        job = Job(
            idempotency_key=(
                f"check-job-store-{uuid4()}"
            ),
            state=JobState.QUEUED,
            prompt="Describe this test image.",
            image_bucket="multimodal-inputs",
            image_object_key=f"inputs/{uuid4()}",
            image_content_type="image/jpeg",
            image_size_bytes=1024,
        )

        database.add(job)
        database.commit()
        database.refresh(job)

        print("Job store check passed")
        print(f"job_id: {job.job_id}")
        print(f"request_id: {job.request_id}")
        print(f"state: {job.state.value}")
        print(f"image_bucket: {job.image_bucket}")
        print(f"image_object_key: {job.image_object_key}")
        print(f"image_content_type: {job.image_content_type}")
        print(f"image_size_bytes: {job.image_size_bytes}")
        print(f"created_at: {job.created_at}")

        database.delete(job)
        database.commit()

        print("Cleanup completed")

    finally:
        database.close()


if __name__ == "__main__":
    main()
