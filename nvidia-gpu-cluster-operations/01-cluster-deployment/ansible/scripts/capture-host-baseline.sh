#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
  pwd
)"

PROJECT_ROOT="$(
  cd -- "${SCRIPT_DIR}/.."
  pwd
)"

ANSIBLE_ROOT="${PROJECT_ROOT}"

HARDWARE_PROFILE_ID="${HARDWARE_PROFILE_ID:-hw-rtx4090-4gpu-pcie-r01}"
EXPERIMENT_ID="${EXPERIMENT_ID:-exp-host-baseline-ansible-r01}"
RUN_TIMESTAMP="$(date -u +'%Y%m%dt%H%M%Sz')"
RUN_ID="run-${EXPERIMENT_ID}-${RUN_TIMESTAMP}"

RUN_ROOT="${PROJECT_ROOT}/evidence/${HARDWARE_PROFILE_ID}/${EXPERIMENT_ID}/${RUN_ID}"
RAW_DIR="${RUN_ROOT}/raw"
NORMALIZED_DIR="${RUN_ROOT}/normalized"

mkdir -p "${RAW_DIR}" "${NORMALIZED_DIR}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_file() {
  [[ -f "$1" ]] || fail "Required file does not exist: $1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 ||
    fail "Required command is unavailable: $1"
}

require_command ansible
require_command ansible-playbook
require_command ansible-inventory
require_command shasum -a 256

require_file "${ANSIBLE_ROOT}/inventory/hosts.yaml"
require_file "${ANSIBLE_ROOT}/playbooks/host-baseline.yaml"
require_file "${ANSIBLE_ROOT}/playbooks/validate-host-baseline.yaml"

export ANSIBLE_CONFIG="${ANSIBLE_ROOT}/ansible.cfg"

run_playbook() {
  local playbook="$1"
  local log_file="$2"

  echo "Running ${playbook}"

  ANSIBLE_LOG_PATH="${log_file}" \
    ansible-playbook \
      -i "${ANSIBLE_ROOT}/inventory/hosts.yaml" \
      "${ANSIBLE_ROOT}/playbooks/${playbook}"
}

ansible --version \
  > "${RAW_DIR}/ansible-version.txt"

ansible-inventory \
  -i "${ANSIBLE_ROOT}/inventory/hosts.yaml" \
  --graph \
  > "${RAW_DIR}/inventory-graph.txt"

run_playbook \
  "host-baseline.yaml" \
  "${RAW_DIR}/first-run.log"

run_playbook \
  "validate-host-baseline.yaml" \
  "${RAW_DIR}/validation.log"

run_playbook \
  "host-baseline.yaml" \
  "${RAW_DIR}/second-run.log"

cat > "${NORMALIZED_DIR}/result.yaml" <<EOF
schema_version: "1.0"
experiment_id: "${EXPERIMENT_ID}"
run_id: "${RUN_ID}"
hardware_profile_id: "${HARDWARE_PROFILE_ID}"
status: "captured"
verdict: "pending-review"
EOF

(
  cd "${RUN_ROOT}"

  find raw normalized \
    -type f \
    -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 \
    > sha256sums.txt
)

echo
echo "Host baseline capture completed."
echo "Run ID: ${RUN_ID}"
echo "Evidence: ${RUN_ROOT}"
