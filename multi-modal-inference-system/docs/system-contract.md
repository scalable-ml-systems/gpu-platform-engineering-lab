# Multimodal Inference System — System Contract

## Purpose

Build a production-style multimodal inference system that accepts image + text requests, executes them on a GPU-backed inference service, and handles failures and overload predictably.

## Request Contract

**Input**

* One image
* One text prompt

**Output**

* Generated text response

**Inference runtime**

* vLLM
* Vision-language model

**Execution model**

* Asynchronous job processing

## Job States

```text
RECEIVED
   ↓
VALIDATED
   ↓
QUEUED
   ↓
RUNNING
   ↓
SUCCEEDED
```

Failure path:

```text
RUNNING
   ↓
RETRYING
   ↓
QUEUED

or

FAILED
```

## Reliability Invariants

1. An accepted job must not be silently lost.
2. Client retries must not create duplicate jobs.
3. A worker failure must not permanently strand a job.
4. Retries must be bounded.
5. Invalid requests must not enter the work queue.
6. The system must reject new work when it exceeds its safe operating envelope.

## Request Durability

Job state is stored separately from the inference worker.

Image artifacts are stored outside the worker process.

A worker crash must not remove the durable job record or source image.

## Idempotency

Clients provide an idempotency key.

Repeated requests using the same key return the existing job instead of creating duplicate inference work.

## Failure Recovery

Workers claim jobs for a bounded period.

If a worker disappears while processing a job, the claim expires and the job becomes eligible for retry.

Permanent request errors are not retried.

Transient infrastructure or inference failures may be retried within the configured retry budget.

## Backpressure

The system monitors:

* queue depth
* oldest queued job age
* active workers
* inference latency

New requests are rejected when the defined operating limit is exceeded rather than allowing the queue to grow without bound.

## Observability

Every request has a unique request and job identifier.

A request must be traceable through:

```text
API
 ↓
job state
 ↓
queue
 ↓
worker
 ↓
vLLM
 ↓
GPU
```

Required signals:

* request latency
* queue wait time
* inference latency
* job state transitions
* retry count
* error reason
* model/runtime version
* GPU utilization and memory

## Deployment Contract

Every running inference job records the model and runtime version used.

A new model or runtime version must be deployable without immediately replacing the known-good version.

Failed releases must support rollback to the last known-good configuration.

## Initial Scope

Included:

* image + text → text inference
* API request handling
* durable job state
* image storage
* work queue
* inference worker
* multimodal vLLM backend
* idempotency
* retries and worker recovery
* backpressure
* end-to-end observability
* model/runtime rollout and rollback
* one controlled worker failure
* one controlled inference failure
* operating-envelope measurement

Excluded:

* audio
* video
* training
* autoscaling
* multi-model routing
* billing
* advanced multi-tenancy
* Kueue
* DRA

## Done

The build is complete when a user can submit an image + prompt and the system can:

1. persist and track the request,
2. process it through multimodal inference,
3. return the result,
4. recover from a worker failure,
5. prevent duplicate work,
6. reject overload before uncontrolled queue growth,
7. trace the request across the full execution path, and
8. roll back a bad model/runtime release.

