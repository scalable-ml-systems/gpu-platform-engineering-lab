def process_message(
    redis_client,
    object_store,
    executor,
    message_id,
    fields,
) -> None:

    event = parse_event(fields)

    with SessionLocal() as database:
        job = claim_job(
            database,
            job_id=event.job_id,
            worker_id=WORKER_ID,
        )

    if job is None:
        handle_unclaimable_message(
            redis_client,
            event,
            message_id,
        )
        return

    image_bytes = object_store.get_object(
        job.image_object_key
    )

    result = executor.generate(
        prompt=job.prompt,
        image_bytes=image_bytes,
        content_type=job.image_content_type,
    )

    with SessionLocal() as database:
        completed = complete_job(
            database,
            job_id=job.job_id,
            worker_id=WORKER_ID,
            result=result,
        )

    if not completed:
        raise RuntimeError(
            "worker lost job ownership"
        )

    redis_client.xack(
        settings.REDIS_STREAM_KEY,
        settings.REDIS_CONSUMER_GROUP,
        message_id,
    )

from multimodal_inference.inference.vllm_executor import (
    VLLMInferenceExecutor,
)
from multimodal_inference.worker.consumer import (
    run_forever,
)


def main() -> None:
    executor = VLLMInferenceExecutor()

    run_forever(
        executor=executor
    )


if __name__ == "__main__":
    main()
