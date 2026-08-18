from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import Session

from multimodal_inference.storage.models import (
    Job,
    JobState,
)


def claim_job(
    database: Session,
    *,
    job_id: UUID,
    worker_id: str,
) -> Job | None:

    statement = (
        update(Job)
        .where(
            Job.job_id == job_id,
            Job.state == JobState.QUEUED,
        )
        .values(
            state=JobState.RUNNING,
            worker_id=worker_id,
            attempt_count=Job.attempt_count + 1,
            started_at=datetime.now(
                timezone.utc
            ),
        )
        .returning(Job)
    )

    job = database.scalar(statement)

    database.commit()

    return job
