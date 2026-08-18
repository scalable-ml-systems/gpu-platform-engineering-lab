from multimodal_inference.messaging.outbox_dispatcher import (
    run_forever,
)


if __name__ == "__main__":
    try:
        run_forever()

    except KeyboardInterrupt:
        print("dispatcher stopped")
