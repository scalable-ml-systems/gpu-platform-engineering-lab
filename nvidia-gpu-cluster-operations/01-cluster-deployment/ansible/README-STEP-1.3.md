# Step 1.3 — Ansible Host Baseline

## Purpose

Prepare a fresh Ubuntu 24.04 RTX 4090 node for k3s.

## Changes

- installs a small prerequisite package set;
- disables swap;
- loads `overlay` and `br_netfilter`;
- enables required sysctl values;
- enables time synchronization;
- validates four RTX 4090 GPUs and one R580 driver version.

## Does not change

- NVIDIA driver;
- CUDA toolkit;
- Kubernetes;
- NVIDIA container runtime;
- NVIDIA device plugin.

## Run

```bash
cp inventory/hosts.example.yaml inventory/hosts.yaml
# Edit inventory/hosts.yaml

./scripts/run-host-baseline.sh
```

Run it twice. The second execution should report no unexpected changes.
