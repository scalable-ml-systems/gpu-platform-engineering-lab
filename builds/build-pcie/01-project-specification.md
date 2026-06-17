# 01 — Project Specification

## Build Name

Build8 V1-A — NVIDIA PCIe Multi-GPU Platform Foundations

## Repository

gpu-platform-engineering-lab

## Objective

Establish and validate an NVIDIA Kubernetes GPU substrate on an 4× RTX 4090 PCIe multi-GPU node.

The build compares the legacy NVIDIA extended-resource path with DRA ResourceClaim-based allocation where supported, then validates Kueue admission, PCIe topology behavior, NCCL communication, vLLM degradation, OOM lifecycle, observability, Golden Path DevEx, and FinOps.

## Hardware

- GPU: 4× NVIDIA RTX 4090
- GPU memory: 24 GB per GPU
- Topology: PCIe multi-GPU
- NVLink/NVSwitch: not claimed in this build

## Explicit Boundary

This is a PCIe topology build.

It does not claim:

- NVLink-aware scheduling
- NVSwitch-aware scheduling
- InfiniBand
- RoCE
- GPUDirect RDMA
- multi-node NCCL

NVLink/NVSwitch validation is scoped separately as a focused add-on experiment.

## Kubernetes Target

Preferred:

- Kubernetes v1.35+

Acceptable:

- Kubernetes v1.33/v1.34 if DRA features are available and limitations are documented

Fallback:

- Legacy NVIDIA device plugin path remains the production baseline if DRA is unavailable.

## Definition of Done

The build is complete when the operator can prove and explain:

1. how an 4× RTX 4090 node appears to Kubernetes;
2. why this is PCIe topology, not NVLink topology;
3. how `nvidia.com/gpu` allocation works;
4. how DRA changes allocation semantics where supported;
5. how Kueue admits, queues, and blocks workloads;
6. how ResourceFlavor encodes fabric policy;
7. how NCCL performance changes across GPU groupings;
8. how vLLM degrades under KV-cache pressure;
9. how CUDA OOM differs from Kubernetes OOMKilled;
10. how signals map to operator action;
11. how developers consume the platform through a Golden Path;
12. how GPU-hours are saved through admission control.
