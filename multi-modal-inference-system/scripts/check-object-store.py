from pathlib import Path

import requests

from multimodal_inference.storage.object_store import (
    S3ObjectStore,
)


def main() -> None:
    source = Path(
        "tests/assets/sample.jpg"
    )
    original = source.read_bytes()

    store = S3ObjectStore()

    ticket = store.create_upload_ticket(
        "image/jpeg"
    )

    response = requests.post(
        ticket.url,
        data=ticket.fields,
        files={
            "file": (
                source.name,
                original,
                "image/jpeg",
            )
        },
        timeout=30,
    )

    response.raise_for_status()

    metadata = store.head(
        ticket.object_key
    )

    assert metadata["ContentLength"] == len(
        original
    )

    assert metadata["ContentType"] == "image/jpeg"

    download_url = store.create_download_url(
        ticket.object_key
    )

    downloaded = requests.get(
        download_url,
        timeout=30,
    )

    downloaded.raise_for_status()

    assert downloaded.content == original

    store.delete(
        ticket.object_key
    )

    print("object store check: PASS")


if __name__ == "__main__":
    main()
