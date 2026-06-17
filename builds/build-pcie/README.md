# Build 8 V1-A — NVIDIA PCIe Multi-GPU Platform Foundations

## Objective

Validate a production-style Kubernetes GPU platform on an 4× RTX 4090 PCIe multi-GPU node.

## Hardware

- GPU: 4× NVIDIA RTX 4090
- GPU memory: 24 GB per GPU
- Topology class: PCIe multi-GPU
- NVLink/NVSwitch: out of scope for this build

## What This Build Proves

1. How NVIDIA GPUs appear through the legacy `nvidia.com/gpu` path.
2. How DRA changes the GPU resource lifecycle where supported.
3. How Kueue admits, queues, and blocks GPU workloads.
4. How ResourceFlavor can encode PCIe versus NVLink placement policy.
5. How NCCL performance changes across PCIe GPU groupings.
6. How vLLM degrades under KV-cache pressure.
7. How CUDA OOM differs from Kubernetes OOMKilled.
8. How observability signals map to operator actions.
9. How to expose the platform through a developer Golden Path.
10. How GPU waste can be reduced with admission control.

## Experiment Suite

1. Legacy NVIDIA GPU Resource Path
2. DRA ResourceClaim Evaluation
3. Kueue Admission: Job Fits Quota
4. Kueue Queue Blockade: Job Exceeds Quota
5. Fabric-Aware Placement: PCIe Allowed vs NVLink Unsatisfied
6. PCIe Topology Discovery
7. NCCL PCIe All-Reduce Matrix
8. vLLM Baseline Inference
9. vLLM KV-Cache Degradation and Latency Cliff
10. OOM Lifecycle: Container OOMKilled vs CUDA OOM
11. Observability, Failure Taxonomy, Golden Path, and FinOps Synthesis
