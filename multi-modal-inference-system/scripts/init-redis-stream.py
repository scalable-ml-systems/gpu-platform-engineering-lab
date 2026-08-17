from redis.exceptions import ResponseError

from multimodal_inference import settings
from multimodal_inference.messaging.redis_stream import (
    create_redis_client,
)


def main() -> None:
    client = create_redis_client()

    client.ping()

    try:
        client.xgroup_create(
            name=settings.REDIS_STREAM_KEY,
            groupname=settings.REDIS_CONSUMER_GROUP,
            id="0-0",
            mkstream=True,
        )

        print(
            "consumer group created: "
            f"{settings.REDIS_CONSUMER_GROUP}"
        )

    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise

        print(
            "consumer group already exists: "
            f"{settings.REDIS_CONSUMER_GROUP}"
        )

    print(
        f"stream ready: "
        f"{settings.REDIS_STREAM_KEY}"
    )


if __name__ == "__main__":
    main()
