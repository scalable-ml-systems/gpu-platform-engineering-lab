# Architecture Decision Index

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Use k3s instead of kubeadm | Accepted |
| ADR-002 | Use NVIDIA device plugin instead of the full GPU Operator | Accepted |
| ADR-003 | Use Kueue for admission and quota | Accepted |
| ADR-004 | Use standard Kubernetes primitives instead of a custom CRD | Accepted |
| ADR-005 | Use Ansible for host and cluster bootstrap | Accepted |
| ADR-006 | Use fixed-replica vLLM without autoscaling | Accepted |
| ADR-007 | Treat guest-visible hardware capability as authoritative | Accepted |

## Change Rule

A new ADR is required when a change affects:

- Kubernetes distribution;
- NVIDIA integration path;
- scheduling or admission framework;
- qualification state model;
- bootstrap automation;
- inference runtime operating model;
- source of truth for hardware capability.

Accepted ADRs are not rewritten to hide prior decisions. Supersede them with a new ADR and preserve the original.
