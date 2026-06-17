# GPU Platform Engineering Lab

This repository documents a practical GPU platform engineering lab for Kubernetes-based AI infrastructure.

The goal is not only to run GPU workloads, but to understand and validate the platform behaviors that matter in production:

- GPU resource lifecycle
- NVIDIA device plugin allocation
- DRA ResourceClaim-based allocation
- Kueue admission and quota control
- topology-aware placement
- NCCL communication behavior
- vLLM inference degradation
- CUDA OOM versus Kubernetes OOMKilled
- observability signals mapped to operator action
- developer-facing Golden Path abstractions
- GPU cost and waste prevention

## Active Build

Build 8 V1-A — NVIDIA PCIe Multi-GPU Platform Foundations

Hardware target: 8× RTX 4090  
Topology class: PCIe multi-GPU  
Primary experiments: Kueue, DRA, NCCL, vLLM, OOM lifecycle, observability, Golden Path, FinOps
