# ADR-005 — Use Ansible for Host and Cluster Bootstrap

- **Status:** Accepted
- **Date:** 2026-07-29

## Context

The project must reproduce host configuration and k3s installation on provider-supplied GPU nodes.

The infrastructure provider may not expose a Terraform-compatible provisioning API, while shell-only automation would be harder to make idempotent and reviewable.

## Decision

Use:

- Ansible for host packages, containerd, NVIDIA runtime configuration, k3s bootstrap, and baseline validation;
- versioned Kubernetes manifests or Helm values for cluster add-ons;
- shell scripts for experiment execution and evidence collection.

## Consequences

### Positive

- Idempotent host configuration.
- Clear task ordering and change visibility.
- Appropriate for SSH-accessible rented nodes.

### Trade-offs

- Does not provision the provider VM itself.
- Provider allocation remains a manual or provider-specific step.
- Ansible dependencies and collections must be pinned.

## Rejected Alternatives

- Terraform without a provider API.
- Large monolithic shell bootstrap script.
- Image baking or Packer for this first implementation.

## Revisit When

Revisit if the provider exposes an API suitable for Terraform or if immutable node images become necessary for fleet-scale deployment.
