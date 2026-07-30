# ADR-002 — Use NVIDIA Device Plugin Instead of the Full GPU Operator

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

The provider supplies a working NVIDIA driver on the GPU node. The project needs Kubernetes GPU resource registration and workload access, but does not need to demonstrate the entire NVIDIA GPU Operator lifecycle.

Installing the full GPU Operator would introduce driver management, toolkit management, node feature discovery, operator policies, and additional controllers that are not necessary for the core experiments.

## Decision

Use:

- the provider-supplied NVIDIA driver;
- NVIDIA Container Toolkit;
- NVIDIA Kubernetes device plugin;
- DCGM Exporter deployed separately.

The project must verify compatibility instead of replacing a working provider driver by default.

## Consequences

### Positive

- Keeps the NVIDIA integration path explicit and understandable.
- Reduces moving parts during qualification and incident drills.
- Avoids conflating provider driver management with Kubernetes GPU allocation.

### Trade-offs

- Does not demonstrate the GPU Operator's integrated lifecycle.
- Driver upgrades remain outside Kubernetes automation in this build.

## Rejected Alternative

**Full NVIDIA GPU Operator**

Rejected because the project is focused on operating GPU workloads and diagnosing capability, not showcasing every NVIDIA cluster add-on.

## Revisit When

Revisit if a later build requires:

- Kubernetes-managed driver lifecycle;
- MIG Manager;
- Node Feature Discovery integration;
- validator workflows;
- fleet-wide upgrade and rollback experiments.
