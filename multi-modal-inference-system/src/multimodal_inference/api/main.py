from fastapi import FastAPI

from multimodal_inference.api.jobs import (
    router as jobs_router,
)
from multimodal_inference.api.uploads import (
    router as uploads_router,
)


app = FastAPI(
    title="Multimodal Inference System",
)


app.include_router(
    uploads_router
)

app.include_router(
    jobs_router
)
