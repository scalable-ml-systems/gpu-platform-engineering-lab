Evidence Contract

Purpose

The evidence contract defines how this project captures, stores, validates,sanitizes, and references operational evidence.

The core rule is:

Raw evidence is immutable. Normalized results and operator interpretation areseparate artifacts that must reference their sources.

This contract applies to host inventory, GPU topology, P2P matrices, NCCL logs,Kubernetes state, Kueue admission, training and inference metrics, incidenttimelines, approvals, and requalification results.

Evidence Classes

Raw

Direct output from a system, application, API, or command. Raw evidence is neveredited in place.

Normalized

Structured data extracted from raw artifacts, such as an experiment result,hardware profile, or qualification result.

Derived

A calculation based on raw or normalized evidence, such as median NCCLbandwidth, protected GPU-hours, or recovery duration.

Interpretive

An operator conclusion, RCA, decision record, or production caveat. Interpretiveevidence must distinguish observed fact from inference.

Immutability and Sealing

Evidence progresses through:

draft → collecting → sealed

Before sealing:

required artifacts exist;

sanitization is complete;

artifact sizes and SHA-256 hashes are recorded;

references resolve;

an operator reviews completeness and consistency.

After sealing, artifacts are immutable. Corrections require a supersedingevidence manifest rather than silent replacement.

Integrity

SHA-256 is the project-wide integrity algorithm. Every sealed artifact records:

repository-relative path;

byte size;

SHA-256 hash;

UTC capture time;

producer;

command, query, or Kubernetes resource;

sanitization state;

source artifacts when derived.

Clock Policy

All timestamps use UTC in this form:

YYYY-MM-DDTHH:MM:SSZ

The manifest records the clock source because host, Kubernetes, and Prometheusclocks may differ.

Sanitization

Before committing or publishing evidence, inspect it for credentials, tokens,private keys, account IDs, provider identifiers, IP addresses, kubeconfigcontents, registry credentials, model access tokens, user names, and personaldata.

Do not silently edit a raw artifact. When redaction is required:

preserve the original outside the public repository when appropriate;

create a sanitized copy;

record the redaction category, replacement, and reason;

hash the sanitized published artifact;

mark it as sanitized.

Retention

Small sanitized evidence may be committed. Large raw logs should be compressed,stored externally with checksums, or excluded when they add little value.Normalized results must not cite deleted evidence without a documented retentiondecision.

Directory Layout

results/<profile-or-domain>/<experiment-id>/
├── evidence-manifest.yaml
├── raw/
├── normalized/
├── derived/
└── operator-conclusion.md

Incident evidence uses:

results/incidents/<incident-id>/
├── evidence-manifest.yaml
├── raw/
├── normalized/
├── timeline/
└── post-incident-review.md

Chain of Evidence

Every public claim should resolve through:

claim
→ operator conclusion
→ experiment result or incident report
→ evidence manifest
→ raw artifact
→ SHA-256 integrity record

Portfolio-Ready Rule

A result is portfolio-ready only when:

required raw artifacts exist;

normalized output exists;

evidence references resolve;

sanitization review passes;

hashes are recorded;

operator review is complete;

limitations are documented.

Prohibited Practices

Do not:

edit raw logs for readability;

overwrite earlier runs;

commit secrets;

use screenshots as the only evidence when machine-readable output exists;

copy metrics manually without the source query;

claim a mean from one run;

mix artifacts from different hardware profiles;

accept an artifact whose hash no longer matches;

present a synthetic fault as a physical hardware failure.
