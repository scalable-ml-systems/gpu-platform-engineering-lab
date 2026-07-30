# ADR-004 — Use Standard Kubernetes Primitives Instead of a Custom Qualification CRD

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

The platform must expose hardware qualification and scheduler eligibility. A custom CRD could model this state, but it would also require API design, versioning, controllers, conversion, validation, and lifecycle ownership.

The initial build needs a working operational path, not a generalized platform API.

## Decision

Use:

- node labels for stable scheduler-facing capability;
- node annotations for profile IDs, reasons, timestamps, and measured summaries;
- `NoSchedule` taints for scheduler exclusion;
- ConfigMaps and result files for detailed qualification output;
- Kubernetes Events for operator-visible transitions;
- Prometheus metrics for history and alerting.

Do not create a qualification CRD in V1.

## Consequences

### Positive

- Uses well-understood Kubernetes mechanisms.
- Keeps the build small and observable.
- Allows Kueue ResourceFlavors to consume qualification labels directly.

### Trade-offs

- No strongly typed Kubernetes API for qualification records.
- Large or historical results must live outside labels and annotations.
- Multi-node fleet workflows may eventually outgrow this model.

## Rejected Alternative

**Custom qualification CRD and controller API**

Rejected because the built-in primitives are sufficient for the current node count and experiments.

## Revisit When

Revisit after concrete evidence shows the need for:

- typed status history;
- multi-stage conditions;
- fleet queries;
- API versioning;
- external integrations that require a formal Kubernetes resource.
