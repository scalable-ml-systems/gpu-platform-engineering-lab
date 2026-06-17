# 03 — Device Plugin vs DRA

## Objective

Compare the legacy NVIDIA `nvidia.com/gpu` extended-resource path with the DRA ResourceClaim-based path where supported.

---

# Experiment 1 — Legacy NVIDIA GPU Resource Path

## Result

Completed.

Kubernetes successfully reports NVIDIA GPUs through the legacy extended-resource path.

Expected evidence:

- `results/legacy-device-plugin/node-allocatable-gpus.txt`
- `results/legacy-device-plugin/nvidia-device-plugin-pods.txt`
- `results/legacy-device-plugin/gpu-pod-logs.txt`
- `results/legacy-device-plugin/gpu-pod-describe.txt`

## Legacy Lifecycle

```text
NVIDIA driver
  -> NVIDIA container runtime
  -> NVIDIA device plugin
  -> Kubernetes node allocatable resource: nvidia.com/gpu
  -> Pod requests nvidia.com/gpu
  -> Scheduler places pod
  -> GPU device is mounted into container
Operational Interpretation

The legacy device plugin path is the production compatibility baseline. It exposes GPU count through nvidia.com/gpu, but it does not by itself express rich placement intent such as PCIe topology, NVLink requirement, or workload-specific fabric policy.

Experiment 2 — DRA ResourceClaim Evaluation
Question

Can this Kubernetes cluster allocate NVIDIA GPUs using Dynamic Resource Allocation?

DRA Lifecycle Under Evaluation
ResourceClass / DeviceClass
  -> ResourceClaim or ResourceClaimTemplate
  -> Pod references claim
  -> DRA driver allocates suitable device
  -> Kubernetes schedules pod to a node that can access the allocated device
Evidence Files
results/dra/kubectl-version.yaml
results/dra/dra-api-discovery.txt
results/dra/api-resources-resource.txt
results/dra/api-resources-claim.txt
results/dra/resourceclass-before.txt
results/dra/resourceclaim-before.txt
results/dra/deviceclass-before.txt
results/dra/resourceslice-before.txt
results/dra/nvidia-dra-pods-before.txt
Result Classification

One of the following will be recorded:

A. DRA works end-to-end.
B. DRA APIs exist, but NVIDIA DRA driver is not installed or not compatible.
C. DRA APIs are unavailable or incomplete in this cluster.
D. DRA is technically available but not selected for V1-A due to operational risk.
Decision Rule

Legacy nvidia.com/gpu remains the production baseline for this build.

DRA is evaluated as the forward-looking claim-based lifecycle path. The build will not claim full DRA replacement unless ResourceClaim-based GPU allocation is proven on this cluster.
