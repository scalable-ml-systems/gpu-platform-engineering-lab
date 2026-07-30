Hardware Profile Contract

Purpose

A hardware profile is an immutable, evidence-backed description of theguest-visible hardware and capabilities exposed by one GPU node at one capturedpoint in time.

It answers:

What hardware is visible?

How is it exposed to the guest?

What PCIe, NUMA, NVLink, P2P, NIC, and RDMA capabilities are visible?

Which raw evidence supports those observations?

What limitations must an operator understand?

It does not answer:

Whether the node passes a workload qualification threshold.

Whether the scheduler should admit a workload.

Whether a measured NCCL result is acceptable.

Whether the node is generally “dev” or “prod.”

Those decisions belong to qualification profiles and qualification results.

Contract Boundary

hardware profile
  = observed inventory + exposed capabilities + evidence

qualification profile
  = required checks + thresholds + workload-class policy

qualification result
  = pass/fail evaluation for one node and profile

Authority Rule

The guest-visible topology is authoritative for this project.

Do not infer NVLink, NVSwitch, PCIe P2P, RDMA, or GPUDirect capability from:

GPU product name;

physical form factor;

provider marketing;

theoretical hardware specifications.

Record what the guest can actually observe and use.

Lifecycle

A profile progresses through:

draft → discovered → verified → superseded

A verified profile is not edited in place when the hardware exposure,virtualization mode, topology, or provider configuration changes. Create a newrevision and link it through supersedes_profile_id.

Required Evidence

A verified profile must reference evidence for:

host operating system;

kernel;

virtualization;

CPU and NUMA topology;

memory;

GPU inventory;

GPU topology;

P2P capability matrices;

NVLink status;

NIC inventory;

RDMA inventory when applicable.

Evidence paths must be repository-relative, and committed evidence should besanitized.

Null Values

Use null when a value has not yet been discovered.

Use an explicit status such as unsupported, unavailable, or not-testedwhen the capability was evaluated and that state is known.

Do not use null to hide a failed or unavailable capability.

Profile Identity

Pattern:

hw-<gpu-model>-<gpu-count>gpu-<topology-or-mode>-r<run>

Canonical initial profiles:

hw-rtx4090-4gpu-pcie-r01
hw-a100-4gpu-passthrough-r01

The provider instance reference may be stored as metadata, but it must not becomethe permanent profile ID.

Qualification Separation

A hardware profile may truthfully record:

nvlink:
  exposed: false
  status: unavailable

It must not directly declare:

collective_qualified: false

Scheduler eligibility belongs to qualification output, not hardware inventory.
