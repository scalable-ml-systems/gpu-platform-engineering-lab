# Multi-modal Inference System — Scope

## Repository

```text
gpu-platform-engineering-lab/
└── Multi-modal-inference-system/
```

## Objective

Build a production-style multimodal inference system that accepts an image and text prompt, executes inference on a GPU-backed vision-language model, and handles requests reliably under failures and load.

The project is designed to demonstrate end-to-end systems engineering, not GPU tooling setup.

## Primary Use Case

A client submits:

```text
image + text prompt
```

The system returns:

```text
generated text
```

Inference runs through a multimodal vLLM backend.

## System Flow

```text
Client
  ↓
API
  ↓
Persist job + image
  ↓
Queue
  ↓
Worker
  ↓
vLLM multimodal inference
  ↓
GPU
  ↓
Persist result
  ↓
Client retrieves result
```

## Core Components

### API Service

Responsibilities:

* accept image + text requests
* validate input
* generate request and job IDs
* enforce idempotency
* apply request limits
* expose job status and results

### Job Store

Stores:

* job ID
* request state
* timestamps
* retry count
* model version
* runtime version
* failure reason
* result metadata

Postgres will be used for durable job state.

### Image Storage

Images are stored separately from job metadata.

Workers retrieve the image using the stored artifact reference.

### Work Queue

Provides:

* pending work
* worker claiming
* retry scheduling
* backpressure signals

Redis will be used for the initial implementation.

### Inference Worker

Responsibilities:

* claim jobs
* retrieve image and prompt
* invoke vLLM
* enforce timeout
* classify failures
* persist result
* update job state

### Multimodal Inference Backend

vLLM serves one vision-language model.

Initial workload:

```text
image + text → text
```

### Observability

The system must correlate:

```text
request
→ job
→ queue
→ worker
→ vLLM
→ Kubernetes
→ GPU
```

Required signals:

* request latency
* queue wait time
* inference latency
* job state
* retry count
* error reason
* queue depth
* model/runtime version
* GPU utilization
* GPU memory

## Job State Model

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

Failure paths:

```text
RUNNING
   ↓
RETRYING
   ↓
QUEUED
```

or:

```text
RUNNING
   ↓
FAILED
```

## Reliability Requirements

1. Accepted jobs must not be silently lost.
2. Client retries must not create duplicate jobs.
3. Worker crashes must not permanently strand jobs.
4. Retries must be bounded.
5. Invalid requests must not enter the work queue.
6. The system must reject new work before queue growth becomes uncontrolled.
7. Every completed job must record the model and runtime version used.

## Failure Scenarios

The build will explicitly test:

### Worker Failure

```text
worker claims job
→ worker terminated
→ lease expires
→ job retried
→ another worker completes job
```

### Inference Failure

Examples:

* inference timeout
* model server unavailable
* GPU OOM

Failures must be classified as retryable or permanent.

### Overload

Increase request arrival rate until the serving limit is reached.

Validate that:

```text
safe load
→ requests accepted

overload
→ requests rejected or shed
```

rather than allowing unlimited queue growth.

### Bad Release

Deploy a candidate model/runtime configuration that causes a measurable regression.

Validate:

```text
candidate fails qualification
→ known-good release remains available
```

## Performance Qualification

Measure the service under increasing concurrency.

Track:

* throughput
* p50/p95 latency
* queue wait
* inference latency
* error rate
* GPU utilization
* GPU memory

The final result must define a safe operating envelope for the tested workload.

## Deployment Platform

Initial environment:

```text
Kubernetes: k3s
GPU: NVIDIA RTX 4090
Container runtime: containerd
Inference runtime: vLLM
Job state: Postgres
Queue: Redis
Observability: OpenTelemetry + Prometheus/Grafana
GPU telemetry: DCGM
```

The existing `nvidia-gpu-cluster-operations` project provides the underlying GPU/Kubernetes infrastructure work.

## In Scope

* image + text → text inference
* asynchronous job API
* durable job state
* image artifact storage
* work queue
* inference worker
* vLLM multimodal backend
* idempotency
* worker leases
* bounded retries
* timeout handling
* failure classification
* backpressure
* load shedding
* request tracing
* inference and GPU metrics
* controlled worker failure
* controlled inference failure
* operating-envelope testing
* model/runtime rollout and rollback

## Out of Scope

* audio
* video
* model training
* multi-model routing
* autoscaling
* billing
* advanced multi-tenancy
* service mesh
* custom Kubernetes operators
* Kueue
* DRA
* topology scheduling

Kueue, DRA, topology, and deeper GPU scheduling work remain in:

```text
nvidia-gpu-cluster-operations/
```

## Primary Portfolio Outcome

The project should demonstrate:

> I built and operated a multimodal inference system end to end, including durable request handling, distributed execution, failure recovery, overload protection, observability, and safe model/runtime deployment.

## Completion Criteria

The build is complete when it can:

1. accept an image and text prompt,
2. persist and track the request,
3. execute multimodal inference,
4. return the result,
5. prevent duplicate jobs,
6. recover from worker failure,
7. handle retryable and permanent inference failures,
8. reject overload before uncontrolled queue growth,
9. trace a request across the full execution path,
10. define a measured serving envelope, and
11. reject or roll back a bad model/runtime release.

