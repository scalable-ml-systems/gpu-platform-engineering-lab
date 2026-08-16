from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.orm import Session

from multimodal_inference.storage.database import (
    SessionLocal,
)
from multimodal_inference.storage.object_store import (
    S3ObjectStore,
)


def get_database() -> Generator[
    Session,
    None,
    None,
]:
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()


@lru_cache
def get_object_store() -> S3ObjectStore:
    return S3ObjectStore()
