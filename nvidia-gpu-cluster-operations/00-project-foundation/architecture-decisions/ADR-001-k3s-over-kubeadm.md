# ADR-001 — Use k3s Instead of kubeadm

- **Status:** Accepted
- **Date:** 2026-07-29
- **Decision owner:** NVIDIA GPU Cluster Operations project

## Context

The project needs a reproducible Kubernetes environment on rented GPU nodes. The primary goal is to demonstrate GPU operations, qualification, scheduling, observability, incidents, and recovery—not to build a production-grade Kubernetes control-plane installation.

Using kubeadm would add certificate management, control-plane bootstrap, networking setup, and upgrade procedures that are not central to this build.

## Decision

Use a pinned k3s release with containerd.

The installation must be automated with Ansible and must record:

- exact k3s version;
- server arguments;
- kubelet version;
- containerd version;
- configuration evidence.

## Consequences

### Positive

- Faster and more reproducible bootstrap.
- Lower operational overhead on rented GPU nodes.
- Retains standard Kubernetes APIs required by Kueue, DCGM, Jobs, labels, taints, Events, and Prometheus.

### Trade-offs

- Does not prove kubeadm-based control-plane construction.
- Some k3s defaults differ from upstream Kubernetes packaging.
- Production migration would require reassessing HA, storage, CNI, security, and upgrade strategy.

## Rejected Alternative

**kubeadm**

Rejected because it adds cluster-bootstrap breadth without materially improving the AI SRE evidence targeted by this build.

## Revisit When

Revisit if the project expands to:

- multi-control-plane HA;
- production cluster upgrades;
- custom CNI or CSI validation;
- enterprise Kubernetes distribution interoperability.
