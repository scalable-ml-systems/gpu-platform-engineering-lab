Experiment Result Contract

Purpose

An experiment result is the normalized, auditable record of one experiment run.

It answers:

What was tested?

On which hardware and software profile?

What was expected?

What actually happened?

Which metrics were observed?

Did the experiment pass, fail, remain partial, or remain inconclusive?

Which evidence supports the verdict?

What is the operational conclusion?

Contract Boundary

hardware profile
  = observed inventory and exposed capability

software manifest
  = exact software, package, and image versions

workload contract
  = fixed workload inputs and operating conditions

experiment result
  = what happened during one run

evidence contract
  = how raw evidence is stored, protected, and referenced

The result references the other contracts. It does not duplicate their fullcontents.

One Result Per Run

Every execution creates one immutable run result.

experiment ID = stable experiment definition
run ID        = one timestamped execution

Example:

exp-nccl-allreduce-4gpu-r01
run-exp-nccl-allreduce-4gpu-r01-20260729t201600z

Result Lifecycle

draft → running → completed
                   ↘ failed
                   ↘ invalid

Use failed when the experiment executed correctly but one or more passcriteria were not met.

Use invalid when the run cannot support a conclusion because of a wrong image,missing prerequisite, malformed parameters, unrelated interruption, or missingevidence.

A failed experiment is valid evidence. An invalid run is not used forqualification or performance conclusions.

Required Sections

Every result contains:

identity and lifecycle;

timing;

hardware and software context;

objective and hypothesis;

execution details;

expected and observed behavior;

quantitative metrics;

criterion-level verdict;

evidence references;

operator conclusion;

approvals when mutation actions are involved.

Pass Criteria

Do not assign pass merely because a command returned exit code zero.

A result passes only when every required criterion passes or the experimentcontract explicitly permits a partial result.

Metrics

Each metric records:

stable metric name;

value;

unit;

aggregation;

source;

bounded labels when needed.

Do not use mean for a single observation.

Verdict Vocabulary

pass
fail
partial
inconclusive
invalid

Use partial when the result is operationally meaningful but not every criterionpassed.

Use inconclusive when evidence is insufficient to decide.

Failure Classification

Use only the project-wide classes:

container-oom
cuda-oom
workload-configuration
nccl-workload-error
fabric-qualification
network-qualification
gpu-runtime
gpu-health
insufficient-evidence

A Kueue workload correctly remaining queued is not a failure and does not requirea failure class.

Evidence Rule

The normalized result never replaces raw evidence.

Every important criterion should reference command output, Kubernetes state,logs, metrics, manifests, dashboard snapshots, or incident timelines.

Operator Conclusion

The conclusion must distinguish:

observed fact;

inference;

operational impact;

next action;

production caveat.

Avoid statements such as the GPUs are slow or Kueue works without definingthe tested conditions and supporting evidence.

Approvals

The approvals section remains empty for read-only experiments.

It is required when the run taints or cordons a node, changes schedulereligibility, launches remediation, restarts approved infrastructure, or restoresa node to service.
