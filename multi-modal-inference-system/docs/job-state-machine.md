# Multi-modal Inference System — Job State Machine

## Purpose

Define the valid states of an inference job and who is allowed to change them.

## States

```text
RECEIVED
    ↓
VALIDATED
    ↓
QUEUED
    ↓
RUNNING
   /     \
  ▼       ▼
SUCCEEDED  FAILED
     ▲
     │
  RETRYING
     │
     └────→ QUEUED
```

| State       | Meaning                                        |
| ----------- | ---------------------------------------------- |
| `RECEIVED`  | API accepted the request                       |
| `VALIDATED` | Input passed validation                        |
| `QUEUED`    | Job is waiting for a worker                    |
| `RUNNING`   | Worker owns the job and is executing inference |
| `RETRYING`  | Previous execution failed but may be retried   |
| `SUCCEEDED` | Result was persisted successfully              |
| `FAILED`    | Job cannot continue                            |

## Allowed Transitions

| From        | To          | Owner             | Trigger                                       |
| ----------- | ----------- | ----------------- | --------------------------------------------- |
| `RECEIVED`  | `VALIDATED` | API               | Request passes validation                     |
| `VALIDATED` | `QUEUED`    | API               | Durable job exists and queue publish succeeds |
| `QUEUED`    | `RUNNING`   | Worker            | Worker claims job                             |
| `RUNNING`   | `SUCCEEDED` | Worker            | Inference and result persistence succeed      |
| `RUNNING`   | `RETRYING`  | Worker / recovery | Retryable failure                             |
| `RETRYING`  | `QUEUED`    | Recovery          | Retry budget remains                          |
| `RUNNING`   | `FAILED`    | Worker            | Permanent failure                             |
| `RETRYING`  | `FAILED`    | Recovery          | Retry budget exhausted                        |

## Terminal States

```text
SUCCEEDED
FAILED
```

Terminal jobs cannot return to an execution state.

## Invalid Transitions

Examples:

```text
RECEIVED  → RUNNING      invalid
QUEUED    → SUCCEEDED    invalid
SUCCEEDED → RUNNING      invalid
FAILED    → RUNNING      invalid
```

The application must reject invalid transitions.

## Worker Failure

If a worker disappears while a job is `RUNNING`:

```text
RUNNING
   ↓ lease expires
RETRYING
   ↓
QUEUED
```

Another worker may then claim the job.

## Retry Rule

A retry occurs only when:

```text
failure is retryable
AND
retry_count < retry_limit
```

Otherwise:

```text
→ FAILED
```

## State Record

Each transition records:

```text
job_id
previous_state
new_state
timestamp
attempt
worker_id
failure_reason
```

## Invariant

> A job has one durable state at any point in time, and every state change must follow an allowed transition.
