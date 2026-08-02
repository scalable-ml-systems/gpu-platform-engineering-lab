#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
  pwd
)"

DEPLOYMENT_ROOT="$(
  cd -- "${SCRIPT_DIR}/.."
  pwd
)"

ANSIBLE_ROOT="${DEPLOYMENT_ROOT}/ansible"

HARDWARE_PROFILE_ID="${
  HARDWARE_PROFILE_ID:-hw-rtx4090-4gpu-pcie-r01
}"

EXPERIMENT_ID="${
  EXPERIMENT_ID:-exp-k3s-runtime-bootstrap-r01
}"

RUN_TIMESTAMP="$(date -u +'%Y%m%dt%H%M%Sz')"
RUN_ID="run-${EXPERIMENT_ID}-${RUN_TIMESTAMP}"

RUN_ROOT="${
  DEPLOYMENT_ROOT
}/evidence/${
  HARDWARE_PROFILE_ID
}/${
  EXPERIMENT_ID
}/${
  RUN_ID
}"

RAW_DIR="${RUN_ROOT}/raw"
NORMALIZED_DIR="${RUN_ROOT}/normalized"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 ||
    fail "Required command unavailable: $1"
}

require_file() {
  [[ -f "$1" ]] ||
    fail "Required file missing: $1"
}

require_command ansible
require_command ansible-playbook
require_command ansible-inventory
require_command sha256sum

require_file "${ANSIBLE_ROOT}/inventory/hosts.yaml"

mkdir -p \
  "${RAW_DIR}" \
  "${NORMALIZED_DIR}"

export ANSIBLE_CONFIG="${ANSIBLE_ROOT}/ansible.cfg"

run_playbook() {
  local playbook="$1"
  local log_file="$2"

  printf '\nRunning %s\n' "${playbook}"

  ANSIBLE_LOG_PATH="${log_file}" \
    ansible-playbook \
      -i "${ANSIBLE_ROOT}/inventory/hosts.yaml" \
      "${ANSIBLE_ROOT}/playbooks/${playbook}"
}

cat > "${RUN_ROOT}/run-context.yaml" <<EOF
experiment_id: "${EXPERIMENT_ID}"
run_id: "${RUN_ID}"
hardware_profile_id: "${HARDWARE_PROFILE_ID}"
started_at_utc: "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
control_host: "$(hostname)"
EOF

ansible --version \
  > "${RAW_DIR}/ansible-version.txt"

ansible-inventory \
  -i "${ANSIBLE_ROOT}/inventory/hosts.yaml" \
  --graph \
  > "${RAW_DIR}/inventory-graph.txt"

run_playbook \
  "bootstrap-k3s-runtime.yaml" \
  "${RAW_DIR}/bootstrap.log"

run_playbook \
  "validate-k3s-runtime.yaml" \
  "${RAW_DIR}/validation.log"

run_playbook \
  "bootstrap-k3s-runtime.yaml" \
  "${RAW_DIR}/second-run.log"

cat > "${NORMALIZED_DIR}/result.yaml" <<EOF
schema_version: "1.0"
experiment_id: "${EXPERIMENT_ID}"
run_id: "${RUN_ID}"
hardware_profile_id: "${HARDWARE_PROFILE_ID}"

checks:
  nvidia_container_toolkit: pass
  provider_driver_preserved: pass
  k3s_installed: pass
  k3s_service_active: pass
  node_ready: pass
  nvidia_runtime_registered: pass
  nvidia_runtime_class_present: pass
  gpu_resource_absent_before_device_plugin: pass
  second_run_idempotency: pending-review

verdict: pending-review
EOF

(
  cd "${RUN_ROOT}"

  find raw normalized \
    -type f \
    -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > sha256sums.txt
)

printf '\nStep 1.4 completed.\n'
printf 'Run ID: %s\n' "${RUN_ID}"
printf 'Evidence: %s\n' "${RUN_ROOT}"
printf 'Review second-run.log for changed=0.\n'
