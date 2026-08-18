import socket
import uuid


WORKER_ID = (
    f"{socket.gethostname()}-{uuid.uuid4()}"
)

def read_messages(
    redis_client,
):
    return redis_client.xreadgroup(
        groupname=settings.REDIS_CONSUMER_GROUP,
        consumername=WORKER_ID,
        streams={
            settings.REDIS_STREAM_KEY: ">"
        },
        count=1,
        block=5000,
    )
