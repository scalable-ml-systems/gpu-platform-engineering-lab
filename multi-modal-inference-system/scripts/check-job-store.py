import uuid

from sqlalchemy.exc import IntegrityError

from multimodal_inference.storage.database import SessionLocal
from multimodal_inference.storage.models import Job, JobState


def main() -> None:
    idempotency_key = f"smoke-{uuid.uuid4()}"

    with SessionLocal() as session:
        job = Job(
            idempotency_key=idempotency_key,
            prompt="Describe this image.",
            image_uri="file:///tmp/test-image.jpg",
        )

        session.add(job)
        session.commit()
        session.refresh(job)

        loaded = session.get(Job, job.job_id)

        assert loaded is not None
        assert loaded.state == JobState.VALIDATED
        assert loaded.retry_count == 0

        print(f"created job: {loaded.job_id}")
        print(f"state: {loaded.state.value}")

        duplicate = Job(
            idempotency_key=idempotency_key,
            prompt="Duplicate request.",
            image_uri="file:///tmp/test-image.jpg",
        )

        session.add(duplicate)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print("duplicate idempotency key: rejected")
        else:
            raise AssertionError(
                "duplicate idempotency key was accepted"
            )

        original = session.get(Job, job.job_id)

        if original:
            session.delete(original)
            session.commit()

    print("job store check: PASS")


if __name__ == "__main__":
    main()
