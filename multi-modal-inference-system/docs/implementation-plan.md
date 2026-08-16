# Multi-modal Inference System — Implementation Plan

## Phase 0 — Freeze Contracts

### Step 0.1 — System contract

Complete.

Artifact:

```text
docs/system-contract.md
```

### Step 0.2 — Request lifecycle

Define:

```text
client
→ API
→ persist job
→ persist image
→ queue
→ worker
→ vLLM
→ result
```

Artifact:

```text
docs/request-lifecycle.md
```

### Step 0.3 — Job state machine

Define valid transitions:

```text
RECEIVED
→ VALIDATED
→ QUEUED
→ RUNNING
→ SUCCEEDED
```

Failure paths:

```text
RUNNING → RETRYING → QUEUED
RUNNING → FAILED
```

Artifact:

```text
docs/job-state-machine.md
```

---

# Phase 1 — Smallest Working Vertical Slice

Goal: one request succeeds end to end.

### Step 1.1 — Repository scaffold

Create:

```text
api/
worker/
inference/
storage/
tests/
deploy/
scripts/
docs/
```

### Step 1.2 — Postgres job model

Store:

```text
job_id
request_id
idempotency_key
state
prompt
image_uri
result
retry_count
model_version
runtime_version
created_at
updated_at
```

### Step 1.3 — Image storage

Initial implementation:

```text
local/object-style storage abstraction
```

API stores the image and persists its URI.

### Step 1.4 — Submit-job API

Implement:

```text
POST /jobs
GET /jobs/{job_id}
```

`POST /jobs`:

```text
validate
→ persist image
→ create job
→ queue job
→ return job_id
```

### Step 1.5 — Redis work queue

Queue contains job identifiers, not image payloads.

### Step 1.6 — Worker

Worker:

```text
claim job
→ mark RUNNING
→ retrieve image
→ call inference backend
→ store result
→ mark SUCCEEDED
```

### Step 1.7 — Multimodal vLLM

Deploy one vision-language model.

Prove:

```text
image + prompt
→ vLLM
→ generated text
```

### Exit gate

One real request must complete:

```text
POST /jobs
→ QUEUED
→ RUNNING
→ SUCCEEDED
→ GET result
```

---

# Phase 2 — Reliability

Goal: requests survive failures predictably.

### Step 2.1 — Idempotency

Same idempotency key:

```text
same job
```

not:

```text
duplicate inference
```

### Step 2.2 — Worker lease

A worker owns a job for a bounded period.

### Step 2.3 — Abandoned-job recovery

Test:

```text
worker claims job
→ kill worker
→ lease expires
→ second worker retries job
→ SUCCEEDED
```

### Step 2.4 — Retry policy

Classify:

```text
retryable
permanent
```

Bound retry count.

### Step 2.5 — Timeout handling

Handle inference requests that exceed their deadline.

---

# Phase 3 — Load Protection

Goal: prevent overload from collapsing the service.

### Step 3.1 — Establish baseline capacity

Measure:

```text
request rate
queue wait
inference latency
throughput
GPU utilization
VRAM
```

### Step 3.2 — Increase concurrency

Run controlled load until latency degrades.

### Step 3.3 — Backpressure

Reject new requests when the operating threshold is exceeded.

Return:

```text
429 Too Many Requests
```

### Step 3.4 — Define operating envelope

Document:

```text
tested workload
safe concurrency
safe throughput
p95 latency
overload threshold
```

---

# Phase 4 — End-to-End Observability

Goal: explain where request time and failures occur.

### Step 4.1 — Correlation IDs

Carry:

```text
request_id
job_id
trace_id
```

through every component.

### Step 4.2 — Distributed tracing

Trace:

```text
API
→ storage
→ queue
→ worker
→ vLLM
```

### Step 4.3 — Service metrics

Measure:

```text
request rate
queue depth
oldest-job age
queue wait
inference latency
error rate
retry rate
```

### Step 4.4 — Infrastructure correlation

Add:

```text
Pod state
vLLM metrics
GPU utilization
GPU memory
```

Build one operational dashboard.

---

# Phase 5 — Controlled Failure Tests

Goal: prove the system behaves correctly when components fail.

Run three incidents:

### Incident 1

```text
worker crash
```

Expected:

```text
job recovered
```

### Incident 2

```text
inference timeout / failure
```

Expected:

```text
classified
→ bounded retry or FAILED
```

### Incident 3

```text
traffic overload
```

Expected:

```text
backpressure activates
→ queue remains bounded
```

Record evidence for each.

---

# Phase 6 — Safe Release

Goal: deploy a changed model/runtime without blindly replacing production.

### Step 6.1 — Version every execution

Every job records:

```text
model_version
runtime_version
```

### Step 6.2 — Deploy candidate

Run:

```text
known-good release
+
candidate release
```

### Step 6.3 — Qualification

Compare:

```text
correctness
errors
latency
throughput
GPU memory
```

### Step 6.4 — Rollback

Introduce one measurable regression.

Expected:

```text
candidate rejected
→ known-good release retained/restored
```

---

# Phase 7 — Package the Portfolio Story

Produce only the artifacts needed to explain the system.

```text
README.md
docs/system-contract.md
docs/request-lifecycle.md
docs/job-state-machine.md
docs/failure-model.md
docs/operating-envelope.md
docs/incident-results.md
docs/release-test.md
```

Final architecture visual:

```text
Client
  ↓
API
  ↓
Postgres + Image Storage
  ↓
Redis
  ↓
Worker
  ↓
vLLM
  ↓
GPU
```

with observability spanning the full request path.

---

# Build Order

```text
Phase 0  Contracts
   ↓
Phase 1  Working vertical slice
   ↓
Phase 2  Reliability
   ↓
Phase 3  Backpressure
   ↓
Phase 4  Observability
   ↓
Phase 5  Failure drills
   ↓
Phase 6  Release / rollback
   ↓
Phase 7  Package and DONE
```

## Immediate Next Step

**Step 0.2 — Define the request lifecycle.**

Do not write infrastructure code yet.

First define exactly what happens from:

```text
POST image + prompt
```

to:

```text
SUCCEEDED + result
```

including which component owns each transition.

