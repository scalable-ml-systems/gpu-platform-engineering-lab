# ADR-006 — Use Fixed-Replica vLLM Without Autoscaling

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

The inference portion must demonstrate that the operator can deploy vLLM, define a workload contract, observe TTFT, latency, queue depth, KV-cache use, and diagnose memory pressure.

Autoscaling would introduce additional questions around metrics, cold starts, load balancing, scale-down safety, and model loading.

## Decision

Deploy one fixed-replica vLLM service with:

- a pinned image digest;
- a fixed model revision;
- fixed model and runtime settings;
- a fixed hardware profile;
- a bounded load test.

Autoscaling is out of scope.

## Consequences

### Positive

- Produces interpretable latency and memory evidence.
- Avoids conflating serving operations with autoscaling design.
- Keeps one inference runtime and one operating contract.

### Trade-offs

- Does not demonstrate dynamic capacity scaling.
- Capacity changes are performed explicitly.

## Rejected Alternative

**Horizontal or event-driven autoscaling**

Rejected because it creates a separate inference capacity-management project.

## Revisit When

Revisit after the fixed-replica service has stable metrics and when autoscaling is a dedicated project objective.
