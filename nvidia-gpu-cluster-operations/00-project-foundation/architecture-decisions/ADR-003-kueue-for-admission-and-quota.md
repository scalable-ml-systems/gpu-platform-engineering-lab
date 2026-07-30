# ADR-003 — Use Kueue for GPU Workload Admission and Quota

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

The build must prove that a multi-GPU workload is admitted only when its complete GPU request fits quota and capability requirements.

The project does not need a replacement scheduler.

## Decision

Use Kueue for:

- LocalQueue and ClusterQueue management;
- GPU quota;
- ResourceFlavor-based capability selection;
- admission and suspension of Kubernetes Jobs.

Use the default Kubernetes scheduler after admission.

## Consequences

### Positive

- Separates admission policy from pod placement.
- Demonstrates queued versus admitted workload state.
- Enables the four-GPU-fit and four-GPU-blocked experiments without adding another scheduler.

### Trade-offs

- Kueue admission is not equivalent to replacing the Kubernetes scheduler.
- Atomic admission must be described precisely and not overstated as universal gang scheduling.
- Readiness behavior may require `waitForPodsReady` for some workloads.

## Rejected Alternatives

- Custom scheduler.
- Volcano.
- YuniKorn.
- A custom admission controller.

Rejected because they add overlapping scheduling systems and unnecessary scope.

## Revisit When

Revisit if indexed Jobs cannot satisfy the distributed workload readiness requirements or if production scheduling needs topology logic unavailable through labels and ResourceFlavors.
