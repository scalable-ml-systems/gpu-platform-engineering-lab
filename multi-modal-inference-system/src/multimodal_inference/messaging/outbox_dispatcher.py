import socket
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from redis.exceptions import RedisError
from sqlalchemy import or_, select, update

from multimodal_inference import settings
from multimodal_inference.messaging.redis_stream import (
    create_redis_client,
)
from multimodal_inference.storage.database import (
    SessionLocal,
)
from multimodal_inference.storage.models import (
    DispatchOutbox,
)


@dataclass(frozen=True)
class ClaimedEvent:
    event_id: uuid.UUID
    job_id: uuid.UUID
    event_type: str
    schema_version: int


DISPATCHER_ID = (
    f"{socket.gethostname()}-{uuid.uuid4()}"
)

def claim_events() -> list[ClaimedEvent]:
    now = datetime.now(timezone.utc)

    lease_expires_at = (
        now
        + timedelta(
            seconds=settings.OUTBOX_CLAIM_SECONDS
        )
    )

    with SessionLocal.begin() as database:
        statement = (
            select(DispatchOutbox)
            .where(
                DispatchOutbox.published_at.is_(None),
                or_(
                    DispatchOutbox.claimed_by.is_(None),
                    DispatchOutbox.claim_expires_at
                    < now,
                ),
            )
            .order_by(
                DispatchOutbox.created_at
            )
            .limit(
                settings.OUTBOX_BATCH_SIZE
            )
            .with_for_update(
                skip_locked=True
            )
        )

        events = list(
            database.scalars(statement)
        )

        claimed: list[ClaimedEvent] = []

        for event in events:
            event.claimed_by = DISPATCHER_ID
            event.claim_expires_at = (
                lease_expires_at
            )

            event.publish_attempts += 1

            claimed.append(
                ClaimedEvent(
                    event_id=event.event_id,
                    job_id=event.job_id,
                    event_type=event.event_type,
                    schema_version=(
                        event.schema_version
                    ),
                )
            )

        return claimed

def publish_event(
    event: ClaimedEvent,
) -> str:

    client = create_redis_client()

    message_id = client.xadd(
        settings.REDIS_STREAM_KEY,
        {
            "event_id": str(
                event.event_id
            ),
            "job_id": str(
                event.job_id
            ),
            "event_type": (
                event.event_type
            ),
            "schema_version": str(
                event.schema_version
            ),
        },
    )

    return str(message_id)

def mark_published(
    event: ClaimedEvent,
    message_id: str,
) -> None:

    now = datetime.now(timezone.utc)

    with SessionLocal.begin() as database:
        result = database.execute(
            update(DispatchOutbox)
            .where(
                DispatchOutbox.event_id
                == event.event_id,
                DispatchOutbox.claimed_by
                == DISPATCHER_ID,
                DispatchOutbox.published_at
                .is_(None),
            )
            .values(
                published_at=now,
                redis_message_id=message_id,
                claimed_by=None,
                claim_expires_at=None,
            )
        )

        if result.rowcount != 1:
            raise RuntimeError(
                "outbox publication ownership lost: "
                f"{event.event_id}"
            )

def mark_published(
    event: ClaimedEvent,
    message_id: str,
) -> None:

    now = datetime.now(timezone.utc)

    with SessionLocal.begin() as database:
        result = database.execute(
            update(DispatchOutbox)
            .where(
                DispatchOutbox.event_id
                == event.event_id,
                DispatchOutbox.claimed_by
                == DISPATCHER_ID,
                DispatchOutbox.published_at
                .is_(None),
            )
            .values(
                published_at=now,
                redis_message_id=message_id,
                claimed_by=None,
                claim_expires_at=None,
            )
        )

        if result.rowcount != 1:
            raise RuntimeError(
                "outbox publication ownership lost: "
                f"{event.event_id}"
            )

def release_claim(
    event: ClaimedEvent,
) -> None:

    with SessionLocal.begin() as database:
        database.execute(
            update(DispatchOutbox)
            .where(
                DispatchOutbox.event_id
                == event.event_id,
                DispatchOutbox.claimed_by
                == DISPATCHER_ID,
                DispatchOutbox.published_at
                .is_(None),
            )
            .values(
                claimed_by=None,
                claim_expires_at=None,
            )
        )

def dispatch_once() -> int:
    events = claim_events()

    published = 0

    for event in events:
        try:
            message_id = publish_event(
                event
            )

            mark_published(
                event,
                message_id,
            )

            print(
                "published "
                f"event_id={event.event_id} "
                f"job_id={event.job_id} "
                f"redis_id={message_id}"
            )

            published += 1

        except RedisError as exc:
            release_claim(event)

            print(
                "redis publish failed "
                f"event_id={event.event_id}: "
                f"{exc}"
            )

    return published

def run_forever() -> None:
    print(
        f"dispatcher started: "
        f"{DISPATCHER_ID}"
    )

    while True:
        count = dispatch_once()

        if count == 0:
            time.sleep(
                settings.DISPATCHER_POLL_SECONDS
            )
