# ADR-007 — Treat Guest-Visible Hardware Capability as Authoritative

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

A virtualized four-A100 node exposed four `A100-SXM4-80GB` devices but did not expose NVLink, PCIe P2P, peer reads, or peer writes. NCCL completed through host shared memory and scaled poorly from two to four GPUs.

Physical product specifications and provider descriptions therefore cannot establish workload fitness.

## Decision

Qualification and scheduling decisions use only capabilities demonstrated inside the workload environment.

Authoritative evidence includes:

- `nvidia-smi topo -m`;
- P2P matrices;
- CUDA P2P tests;
- `nvidia-smi nvlink --status`;
- NCCL transport and measured behavior;
- NIC and RDMA visibility;
- GPU-to-NIC and NUMA locality.

Do not infer exposed capability from GPU model, SXM form factor, theoretical bandwidth, or provider marketing.

## Consequences

### Positive

- Prevents false qualification of premium but poorly exposed hardware.
- Makes workload placement evidence-based.
- Supports honest negative qualification artifacts.

### Trade-offs

- A node may be classified more conservatively than its physical hardware specification suggests.
- Some provider capabilities cannot be claimed without guest-visible evidence.

## Rejected Alternative

**Qualify by GPU model or theoretical product specification**

Rejected because it failed on the observed A100 passthrough node.

## Revisit When

This decision is foundational and should be revisited only if qualification moves outside the guest and gains trusted host, hypervisor, switch, or BMC telemetry.
