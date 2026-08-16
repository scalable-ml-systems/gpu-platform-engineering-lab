# Multi-modal Inference System — Request Lifecycle

## Purpose

Define the request path from client submission to final result, including component ownership and state transitions.

## Request Flow

```text
Client
  ↓
API
  ↓
Validate request
  ↓
Persist image
  ↓
Create job record
  ↓
Queue job
  ↓
Worker claims job
  ↓
Invoke multimodal vLLM
  ↓
Persist result
  ↓
Mark job complete
  ↓
Client retrieves result
```

## Lifecycle

### 1. Request Received

Client sends:

```text
POST /jobs
```

Payload:

* image
* text prompt
* idempotency key

Owner:

```text
API
```

Job state:

```text
RECEIVED
```

---

### 2. Request Validated

API validates:

* image type
* image size
* prompt presence
* request limits
* idempotency key

Invalid requests return an error and stop here.

Valid requests transition:

```text
RECEIVED → VALIDATED
```

Owner:

```text
API
```

---

### 3. Image Persisted

The image is stored outside the job record.

The API receives an image URI:

```text
image_uri
```

Owner:

```text
Storage
```

The job record stores the URI, not the image payload.

---

### 4. Job Persisted

The API creates the durable job record in Postgres.

Required fields include:

```text
job_id
request_id
idempotency_key
prompt
image_uri
state
retry_count
model_version
runtime_version
timestamps
```

State:

```text
VALIDATED
```

Owner:

```text
Postgres
```

The job must exist durably before it enters the queue.

---

### 5. Job Queued

The API publishes:

```text
job_id
```

to Redis.

The queue does not contain the image payload.

State transition:

```text
VALIDATED → QUEUED
```

Owner:

```text
Queue
```

---

### 6. Worker Claims Job

A worker receives the job ID.

It loads the job record and image reference.

State transition:

```text
QUEUED → RUNNING
```

The worker also records a bounded lease.

Owner:

```text
Worker
```

---

### 7. Inference Executed

The worker sends:

```text
image + prompt
```

to the multimodal vLLM backend.

vLLM executes the request on the GPU.

Owner:

```text
Worker → vLLM
```

Possible outcomes:

```text
success
timeout
inference error
GPU/runtime failure
```

---

### 8. Result Persisted

On success, the worker stores the generated text and execution metadata.

State transition:

```text
RUNNING → SUCCEEDED
```

Stored metadata includes:

```text
result
model_version
runtime_version
inference_latency
completed_at
```

Owner:

```text
Worker + Postgres
```

---

### 9. Failure Handling

Retryable failure:

```text
RUNNING
  ↓
RETRYING
  ↓
QUEUED
```

Permanent failure or exhausted retry budget:

```text
RUNNING → FAILED
```

The failure reason is persisted.

---

### 10. Client Retrieves Result

Client requests:

```text
GET /jobs/{job_id}
```

Possible responses:

```text
QUEUED
RUNNING
RETRYING
SUCCEEDED
FAILED
```

A successful response returns the generated text.

Owner:

```text
API
```

## Component Ownership

| Component     | Responsibility                                    |
| ------------- | ------------------------------------------------- |
| API           | validation, idempotency, job creation, status API |
| Postgres      | durable job state                                 |
| Image Storage | image artifact                                    |
| Redis         | pending work                                      |
| Worker        | job execution and recovery                        |
| vLLM          | multimodal model inference                        |
| GPU           | model execution                                   |

## Critical Ordering

The system must preserve this order:

```text
validate
→ persist image
→ persist job
→ enqueue job
```

A job must never be placed in the queue before its durable state exists.

## Successful Request

```text
RECEIVED
→ VALIDATED
→ QUEUED
→ RUNNING
→ SUCCEEDED
```

## Failure Request

```text
RECEIVED
→ VALIDATED
→ QUEUED
→ RUNNING
→ RETRYING
→ QUEUED
```

or:

```text
RUNNING → FAILED
```

## Lifecycle Invariant

> Once the API accepts a request and creates its durable job record, the system must always be able to determine whether that job is queued, running, completed, retrying, or failed.

