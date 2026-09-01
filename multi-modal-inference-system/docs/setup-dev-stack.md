# Local Development Setup

This document describes the local setup for the multimodal inference system.

The local development stack contains:

```text
Client
  ↓
FastAPI API
  ↓
Postgres ── durable Job and DispatchOutbox records
  ↓
Redis Stream ── inference job transport
  ↓
Inference worker
  ↓
MinIO ── uploaded image storage
  ↓
vLLM ── multimodal model inference
```

## Prerequisites

Install the following system dependencies:

```bash
sudo apt update

sudo apt install \
  python3.12-venv \
  postgresql-client-common \
  postgresql-client
```

Docker and Docker Compose must also be available:

```bash
docker --version
docker compose version
```

If Docker commands fail with a permission error for `/var/run/docker.sock`, add the current user to the Docker group:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

> Warning: Docker group membership effectively grants privileged access on the local host. Only add trusted users.

## Create the Python Environment

From the repository root:

```bash
cd ~/gpu-platform-engineering-lab/multi-modal-inference-system
```

Create and activate the project virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Verify that the environment is active:

```bash
which python
python --version
python -m pip --version
```

Expected Python location:

```text
.../multi-modal-inference-system/.venv/bin/python
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m pip install pytest requests
```

For a persistent project setup, declare all runtime dependencies in `pyproject.toml`, including:

```toml
dependencies = [
    "SQLAlchemy==2.0.51",
    "alembic==1.18.5",
    "psycopg[binary]==3.3.4",
    "boto3",
    "python-dotenv",
    "fastapi",
    "uvicorn[standard]",
    "redis[hiredis]==8.0.1",
    "httpx",
    "requests",
]
```

Add test dependencies separately:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]
```

Then install them with:

```bash
python -m pip install -e ".[dev]"
```

## Configure Local Environment

Create a private `.env` file in the repository root:

```bash
cp .env.example .env
chmod 600 .env
vi .env
```

Use local-development configuration similar to this:

```bash
# vLLM
VLLM_API_KEY=replace-with-a-long-random-local-secret
VLLM_BASE_URL=http://127.0.0.1:8001/v1

# Postgres
DATABASE_URL=postgresql+psycopg://multimodal:multimodal@localhost:5432/multimodal

# MinIO / S3-compatible object storage
OBJECT_STORE_ENDPOINT_URL=http://localhost:9000
OBJECT_STORE_BUCKET=multimodal-inputs
OBJECT_STORE_REGION=us-east-1

# Upload policy
OBJECT_STORE_MAX_UPLOAD_BYTES=10485760
OBJECT_STORE_PRESIGN_TTL_SECONDS=300

# MinIO credentials
MINIO_ROOT_USER=multimodal-local
MINIO_ROOT_PASSWORD=change-me-local-only

# Boto3 / application credentials
AWS_ACCESS_KEY_ID=multimodal-local
AWS_SECRET_ACCESS_KEY=change-me-local-only

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_STREAM_KEY=inference.jobs
REDIS_CONSUMER_GROUP=inference-workers

# Dispatcher
OUTBOX_BATCH_SIZE=25
OUTBOX_CLAIM_SECONDS=30
DISPATCHER_POLL_SECONDS=1
```

Generate a strong local vLLM API key:

```bash
openssl rand -hex 32
```

Store the generated value as:

```bash
VLLM_API_KEY=<generated-secret>
```

Do not commit `.env`. Ensure `.gitignore` contains:

```gitignore
.env
.venv/
```

Load the configuration into the active shell before running scripts:

```bash
set -a
source .env
set +a
```

Verify that configuration loaded without printing secrets:

```bash
test -n "${OBJECT_STORE_BUCKET:-}" \
  && echo "OBJECT_STORE_BUCKET is set" \
  || echo "OBJECT_STORE_BUCKET is missing"

test -n "${VLLM_API_KEY:-}" \
  && echo "VLLM_API_KEY is set" \
  || echo "VLLM_API_KEY is missing"
```

## Start vLLM

Start the local vLLM server:

```bash
./scripts/run-vllm-server.sh
```

Or, if the script has not been made executable:

```bash
bash ./scripts/run-vllm-server.sh
```

Verify the vLLM container:

```bash
docker ps
```

Expected service:

```text
multimodal-vllm
```

Verify server health:

```bash
curl -sS http://127.0.0.1:8001/health
curl -sS http://127.0.0.1:8001/version
```

Expected version response:

```json
{
  "version": "0.26.0"
}
```

Verify authenticated OpenAI-compatible API access:

```bash
curl -sS \
  -H "Authorization: Bearer ${VLLM_API_KEY}" \
  http://127.0.0.1:8001/v1/models
```

If this returns `Unauthorized`, confirm that:

1. The current shell has loaded `.env`.
2. The running vLLM container was started with the same `VLLM_API_KEY`.
3. The vLLM container was recreated after changing the key.

## Start MinIO

Start the local object-storage service:

```bash
docker compose \
  -f deploy/local/object-store.compose.yaml \
  --env-file .env \
  up -d
```

Verify the container:

```bash
docker ps
```

Verify MinIO health:

```bash
curl -i http://127.0.0.1:9000/minio/health/live
```

Expected result:

```text
HTTP/1.1 200 OK
```

Initialize the required bucket:

```bash
python scripts/init-object-store.py
```

Validate application access to MinIO:

```bash
python scripts/check-object-store.py
```

The expected bucket is configured by:

```bash
OBJECT_STORE_BUCKET=multimodal-inputs
```

## Start Redis

Start the local Redis service:

```bash
docker compose \
  -f deploy/local/redis.compose.yaml \
  --env-file .env \
  up -d
```

Verify Redis:

```bash
redis-cli -h 127.0.0.1 -p 6379 ping
```

Expected output:

```text
PONG
```

Initialize the Redis Stream and consumer group:

```bash
python scripts/init-redis-stream.py
```

The stream configuration is:

```bash
REDIS_STREAM_KEY=inference.jobs
REDIS_CONSUMER_GROUP=inference-workers
```

## Start PostgreSQL

Run PostgreSQL locally in Docker:

```bash
docker run -d \
  --name multimodal-postgres \
  --restart unless-stopped \
  -p 127.0.0.1:5432:5432 \
  -e POSTGRES_USER=multimodal \
  -e POSTGRES_PASSWORD=multimodal \
  -e POSTGRES_DB=multimodal \
  -v multimodal-postgres-data:/var/lib/postgresql/data \
  postgres:16
```

Watch the startup logs:

```bash
docker logs -f multimodal-postgres
```

Wait until PostgreSQL reports:

```text
database system is ready to accept connections
```

Verify readiness:

```bash
pg_isready \
  -h 127.0.0.1 \
  -p 5432 \
  -U multimodal \
  -d multimodal
```

Expected output:

```text
127.0.0.1:5432 - accepting connections
```

## Apply Database Migrations

Run migrations after PostgreSQL is available:

```bash
alembic upgrade head
```

Confirm the database revision:

```bash
alembic current
alembic heads
```

Validate durable job persistence:

```bash
python scripts/check-job-store.py
```

The job-store validation script must use the current `Job` model fields:

```python
job = Job(
    idempotency_key=f"check-job-store-{uuid4()}",
    state=JobState.QUEUED,
    prompt="Describe this test image.",
    image_bucket="multimodal-inputs",
    image_object_key=f"inputs/{uuid4()}",
    image_content_type="image/jpeg",
    image_size_bytes=1024,
)
```

Do not use the obsolete `image_uri` field.

## Start the API

Find the FastAPI application module:

```bash
rg -n "FastAPI\(" src/multimodal_inference
```

If the application object is defined as:

```python
app = FastAPI(...)
```

in:

```text
src/multimodal_inference/main.py
```

start the API:

```bash
uvicorn multimodal_inference.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload
```

Verify API availability in another terminal:

```bash
curl -sS http://127.0.0.1:8000/openapi.json \
  | python -m json.tool
```

The API should expose routes similar to:

```text
POST /uploads/authorize
POST /jobs
GET  /jobs/{job_id}
```

## Start Dispatcher and Worker

Run each process in a separate terminal.

### Terminal 1: FastAPI API

```bash
source .venv/bin/activate

set -a
source .env
set +a

uvicorn multimodal_inference.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload
```

### Terminal 2: Outbox Dispatcher

```bash
source .venv/bin/activate

set -a
source .env
set +a

python scripts/run-outbox-dispatcher.py
```

The dispatcher publishes durable database outbox records to Redis:

```text
Postgres DispatchOutbox
        ↓
Redis Stream
```

### Terminal 3: Inference Worker

```bash
source .venv/bin/activate

set -a
source .env
set +a

python scripts/run-worker.py
```

The worker performs the inference workflow:

```text
Redis Stream
        ↓
Fetch image from MinIO
        ↓
Call vLLM
        ↓
Write result and state transition to Postgres
```

## Verify Services

Run the available validation scripts:

```bash
python scripts/check-object-store.py
python scripts/check-job-store.py
python scripts/check-vllm-multimodal.py
python scripts/check-job-submission.py
```

Check active containers:

```bash
docker ps
```

Expected local services:

```text
multimodal-vllm
multimodal-postgres
MinIO
Redis
```

Check active listening ports:

```bash
ss -ltn | grep -E ':(5432|6379|8000|8001|9000|9001)\b'
```

Expected ports:

| Service | Port |
|---|---:|
| PostgreSQL | 5432 |
| Redis | 6379 |
| FastAPI API | 8000 |
| vLLM | 8001 |
| MinIO S3 API | 9000 |
| MinIO Console | 9001, if exposed |

## End-to-End Client Workflow

The complete client workflow is:

```text
1. Authorize image upload
2. Upload image directly to MinIO
3. Submit durable inference job
4. Observe QUEUED → RUNNING → SUCCEEDED
5. Read result from GET /jobs/{job_id}
```

### 1. Authorize Upload

```bash
IMAGE_FILE="$HOME/path/to/image.jpg"
CONTENT_TYPE="image/jpeg"

AUTHORIZE_RESPONSE=$(
  curl -sS -X POST \
    http://127.0.0.1:8000/uploads/authorize \
    -H "Content-Type: application/json" \
    -d "{
      \"content_type\": \"${CONTENT_TYPE}\"
    }"
)

printf '%s\n' "$AUTHORIZE_RESPONSE" | python -m json.tool
```

Extract the object key and presigned upload URL using the actual response field names:

```bash
OBJECT_KEY=$(
  printf '%s' "$AUTHORIZE_RESPONSE" \
  | python -c 'import json, sys; print(json.load(sys.stdin)["object_key"])'
)

UPLOAD_URL=$(
  printf '%s' "$AUTHORIZE_RESPONSE" \
  | python -c 'import json, sys; print(json.load(sys.stdin)["upload_url"])'
)
```

### 2. Upload Directly to MinIO

```bash
curl -i -X PUT \
  -H "Content-Type: ${CONTENT_TYPE}" \
  --upload-file "$IMAGE_FILE" \
  "$UPLOAD_URL"
```

Expected response:

```text
HTTP/1.1 200 OK
```

or:

```text
HTTP/1.1 204 No Content
```

The direct-upload pattern keeps image bytes off the API process. The API authorizes a short-lived object upload, and the client sends the file directly to S3-compatible storage. [279][280]

### 3. Submit Job

```bash
PROMPT="Describe this image accurately and concisely."

curl -sS -D /tmp/job-headers.txt \
  -o /tmp/job-response.json \
  -X POST \
  http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: e2e-001" \
  -d "{
    \"object_key\": \"${OBJECT_KEY}\",
    \"prompt\": \"${PROMPT}\"
  }"
```

Inspect the response:

```bash
cat /tmp/job-headers.txt
python -m json.tool /tmp/job-response.json
```

Expected initial response:

```text
HTTP/1.1 201 Created
```

Expected initial state:

```json
{
  "state": "QUEUED"
}
```

Extract the job ID:

```bash
JOB_ID=$(
  python -c '
import json

with open("/tmp/job-response.json") as file:
    print(json.load(file)["job_id"])
'
)

echo "Job ID: ${JOB_ID}"
```

### 4. Poll Job Status

```bash
while true; do
  RESPONSE=$(
    curl -sS \
      "http://127.0.0.1:8000/jobs/${JOB_ID}"
  )

  STATE=$(
    printf '%s' "$RESPONSE" \
    | python -c '
import json
import sys

print(json.load(sys.stdin)["state"])
'
  )

  printf '%s  %s\n' \
    "$(date '+%H:%M:%S')" \
    "$STATE"

  if [[ "$STATE" == "SUCCEEDED" || "$STATE" == "FAILED" ]]; then
    printf '%s\n' "$RESPONSE" | python -m json.tool
    break
  fi

  sleep 2
done
```

Expected state transitions:

```text
QUEUED
   ↓
RUNNING
   ↓
SUCCEEDED
```

Expected final response shape:

```json
{
  "job_id": "...",
  "request_id": "...",
  "state": "SUCCEEDED",
  "image_object_key": "inputs/...",
  "result": "A generated description of the image.",
  "failure_reason": null,
  "model_version": "Qwen/Qwen2.5-VL-7B-Instruct@...",
  "runtime_version": "vllm-0.26.0",
  "created_at": "...",
  "completed_at": "..."
}
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'requests'`

Install the missing Python package in the active virtual environment:

```bash
python -m pip install requests
```

Then add `requests` to `pyproject.toml`.

### `KeyError: 'OBJECT_STORE_BUCKET'`

Load `.env` before running the script:

```bash
set -a
source .env
set +a
```

Verify:

```bash
python -c '
import os

print(os.environ.get("OBJECT_STORE_BUCKET"))
'
```

Expected:

```text
multimodal-inputs
```

### `pg_isready ... no response`

Postgres is not running. Start the `multimodal-postgres` container, then wait for:

```text
database system is ready to accept connections
```

### `Unauthorized` from vLLM

The client API key does not match the key configured in the running vLLM container.

Reload the local key:

```bash
set -a
source .env
set +a
```

Then recreate the vLLM server container using the current `VLLM_API_KEY`.

### Job remains `QUEUED`

Check whether the dispatcher and worker are running:

```bash
ps aux | grep -E \
  "run-outbox-dispatcher|run-worker" \
  | grep -v grep
```

Check Redis:

```bash
redis-cli -h 127.0.0.1 -p 6379 ping
```

Check worker and dispatcher terminal logs for errors.

### Job becomes `FAILED`

Retrieve the durable failure reason:

```bash
curl -sS \
  "http://127.0.0.1:8000/jobs/${JOB_ID}" \
  | python -m json.tool
```

Inspect:

```json
{
  "state": "FAILED",
  "failure_reason": "..."
}
```

## Shutdown

Stop host-run processes with `Ctrl+C` in their respective terminals.

Stop local containers:

```bash
docker stop \
  multimodal-vllm \
  multimodal-postgres
```

Stop MinIO and Redis through Compose:

```bash
docker compose \
  -f deploy/local/object-store.compose.yaml \
  down

docker compose \
  -f deploy/local/redis.compose.yaml \
  down
```

The PostgreSQL data remains in the persistent Docker volume:

```text
multimodal-postgres-data
```

To remove the database data completely:

```bash
docker rm multimodal-postgres
docker volume rm multimodal-postgres-data
```

> Warning: removing the Docker volume permanently deletes all local job records and database state.
