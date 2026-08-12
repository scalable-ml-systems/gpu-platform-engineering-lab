#!/usr/bin/env bash
#
# Step 1.5 — Install and validate the NVIDIA device plugin.
#
# Operator entrypoint:
#   ./01-cluster-deployment/scripts/install-nvidia-device-plugin.sh
#
# Runs from the local Ansible control machine. Configuration changes occur
# on the CloudRift GPU node through Ansible. Evidence remains on the local
# durable filesystem.
#
# Required repository files:
#   ansible/inventory/hosts.yaml
#   ansible/playbooks/install-nvidia-device-plugin.yaml
#   ansible/playbooks/validate-nvidia-device-plugin.yaml
#
# Optional environment overrides:
#   TARGET_GROUP=gpu_nodes
#   HARDWARE_PROFILE_ID=hw-rtx4090-4gpu-pcie-r01
#   EXPERIMENT_ID=exp-device-plugin-r01
#   EXPECTED_GPU_COUNT=4
#   NVDP_RELEASE_NAME=nvdp
#   NVDP_NAMESPACE=nvidia-device-plugin
#
# The chart version belongs in Ansible inventory/group_vars, not here.
# This prevents the shell wrapper and Ansible configuration from drifting.

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ANSIBLE_ROOT="${DEPLOYMENT_ROOT}/ansible"

INVENTORY_FILE="${ANSIBLE_ROOT}/inventory/hosts.yaml"
INSTALL_PLAYBOOK="${ANSIBLE_ROOT}/playbooks/install-nvidia-device-plugin.yaml"
VALIDATE_PLAYBOOK="${ANSIBLE_ROOT}/playbooks/validate-nvidia-device-plugin.yaml"

TARGET_GROUP="${TARGET_GROUP:-gpu_nodes}"
HARDWARE_PROFILE_ID="${HARDWARE_PROFILE_ID:-hw-rtx4090-4gpu-pcie-r01}"
EXPERIMENT_ID="${EXPERIMENT_ID:-exp-device-plugin-r01}"
EXPECTED_GPU_COUNT="${EXPECTED_GPU_COUNT:-4}"
NVDP_RELEASE_NAME="${NVDP_RELEASE_NAME:-nvdp}"
NVDP_NAMESPACE="${NVDP_NAMESPACE:-nvidia-device-plugin}"

RUN_TIMESTAMP="$(date -u +'%Y%m%dt%H%M%Sz')"
RUN_ID="run-${RUN_TIMESTAMP}"

RUN_ROOT="${DEPLOYMENT_ROOT}/evidence/${HARDWARE_PROFILE_ID}/${EXPERIMENT_ID}/${RUN_ID}"
RAW_DIR="${RUN_ROOT}/raw"
NORMALIZED_DIR="${RUN_ROOT}/normalized"

RESULT_FILE="${NORMALIZED_DIR}/result.yaml"
CHECKSUM_FILE="${RUN_ROOT}/sha256sums.txt"

CURRENT_STAGE="preflight"
FINALIZED="false"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  return 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 ||
    fail "Required command is unavailable: $1"
}

require_file() {
  [[ -f "$1" ]] ||
    fail "Required file does not exist: $1"
}

write_checksums() {
  local checksum_command=()

  if command -v sha256sum >/dev/null 2>&1; then
    checksum_command=(sha256sum)
  elif command -v shasum >/dev/null 2>&1; then
    # macOS provides shasum rather than sha256sum.
    checksum_command=(shasum -a 256)
  else
    fail "Neither sha256sum nor shasum is available."
  fi

  (
    cd "${RUN_ROOT}"
    find raw normalized -type f \
      | LC_ALL=C sort \
      | while IFS= read -r artifact; do
          "${checksum_command[@]}" "${artifact}"
        done \
      > "${CHECKSUM_FILE}"
  )
}

write_result() {
  local verdict="$1"
  local failed_stage="${2:-none}"
  local idempotency="${3:-not-evaluated}"

  cat > "${RESULT_FILE}" <<EOF
schema_version: "1.0"
experiment_id: "${EXPERIMENT_ID}"
run_id: "${RUN_ID}"
hardware_profile_id: "${HARDWARE_PROFILE_ID}"
target_group: "${TARGET_GROUP}"
expected_gpu_count: ${EXPECTED_GPU_COUNT}

checks:
  ansible_connectivity: ${ANSIBLE_CONNECTIVITY_STATUS:-not-run}
  device_plugin_install: ${DEVICE_PLUGIN_INSTALL_STATUS:-not-run}
  device_plugin_validation: ${DEVICE_PLUGIN_VALIDATION_STATUS:-not-run}
  evidence_capture: ${EVIDENCE_CAPTURE_STATUS:-not-run}
  second_run_idempotency: ${idempotency}

verdict: "${verdict}"
failed_stage: "${failed_stage}"
EOF
}

finalize_failure() {
  local exit_code="$?"
  trap - ERR

  if [[ "${FINALIZED}" == "true" ]]; then
    exit "${exit_code}"
  fi

  FINALIZED="true"
  mkdir -p "${RAW_DIR}" "${NORMALIZED_DIR}"

  write_result "fail" "${CURRENT_STAGE}" "not-evaluated" || true
  write_checksums || true

  printf '\nStep 1.5 failed during stage: %s\n' "${CURRENT_STAGE}" >&2
  printf 'Evidence retained at: %s\n' "${RUN_ROOT}" >&2

  exit "${exit_code}"
}

trap finalize_failure ERR

run_playbook() {
  local playbook_path="$1"
  local log_path="$2"

  printf '\nRunning %s\n' "$(basename "${playbook_path}")"

  ANSIBLE_LOG_PATH="${log_path}" \
    ansible-playbook \
      -i "${INVENTORY_FILE}" \
      "${playbook_path}"
}

capture_remote() {
  local output_file="$1"
  local remote_command="$2"

  ansible \
    -i "${INVENTORY_FILE}" \
    "${TARGET_GROUP}" \
    --become \
    -m ansible.builtin.shell \
    -a "${remote_command}" \
    > "${RAW_DIR}/${output_file}"
}

mkdir -p "${RAW_DIR}" "${NORMALIZED_DIR}"

cat > "${RUN_ROOT}/run-context.yaml" <<EOF
experiment_id: "${EXPERIMENT_ID}"
run_id: "${RUN_ID}"
hardware_profile_id: "${HARDWARE_PROFILE_ID}"
target_group: "${TARGET_GROUP}"
expected_gpu_count: ${EXPECTED_GPU_COUNT}
nvdp_release_name: "${NVDP_RELEASE_NAME}"
nvdp_namespace: "${NVDP_NAMESPACE}"
started_at_utc: "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
control_host: "$(hostname)"
deployment_root: "${DEPLOYMENT_ROOT}"
EOF

CURRENT_STAGE="local-preflight"

require_command ansible
require_command ansible-playbook
require_command ansible-inventory
require_file "${INVENTORY_FILE}"
require_file "${INSTALL_PLAYBOOK}"
require_file "${VALIDATE_PLAYBOOK}"

export ANSIBLE_CONFIG="${ANSIBLE_ROOT}/ansible.cfg"

ansible --version > "${RAW_DIR}/ansible-version.txt"

ansible-inventory \
  -i "${INVENTORY_FILE}" \
  --graph \
  > "${RAW_DIR}/inventory-graph.txt"

if ! ansible-inventory \
  -i "${INVENTORY_FILE}" \
  --list \
  | grep -q "\"${TARGET_GROUP}\""; then
  fail "Inventory group '${TARGET_GROUP}' was not found in ${INVENTORY_FILE}."
fi

CURRENT_STAGE="ansible-connectivity"

ansible \
  -i "${INVENTORY_FILE}" \
  "${TARGET_GROUP}" \
  -m ansible.builtin.ping \
  > "${RAW_DIR}/ansible-ping.txt"

ANSIBLE_CONNECTIVITY_STATUS="pass"

CURRENT_STAGE="install-device-plugin"

run_playbook \
  "${INSTALL_PLAYBOOK}" \
  "${RAW_DIR}/install.log"

DEVICE_PLUGIN_INSTALL_STATUS="pass"

CURRENT_STAGE="validate-device-plugin"

run_playbook \
  "${VALIDATE_PLAYBOOK}" \
  "${RAW_DIR}/validation.log"

DEVICE_PLUGIN_VALIDATION_STATUS="pass"

CURRENT_STAGE="capture-evidence"

capture_remote \
  "helm-version.txt" \
  'helm version --short'

capture_remote \
  "helm-release.txt" \
  "helm list \
     --kubeconfig /etc/rancher/k3s/k3s.yaml \
     --namespace '${NVDP_NAMESPACE}'"

capture_remote \
  "helm-values.yaml" \
  "helm get values '${NVDP_RELEASE_NAME}' \
     --kubeconfig /etc/rancher/k3s/k3s.yaml \
     --namespace '${NVDP_NAMESPACE}' \
     --all"

capture_remote \
  "device-plugin-workloads.txt" \
  "k3s kubectl \
     --namespace '${NVDP_NAMESPACE}' \
     get daemonsets,pods \
     -o wide"

capture_remote \
  "device-plugin-daemonset.yaml" \
  "k3s kubectl \
     --namespace '${NVDP_NAMESPACE}' \
     get daemonsets \
     -o yaml"

capture_remote \
  "device-plugin-logs.txt" \
  "k3s kubectl \
     --namespace '${NVDP_NAMESPACE}' \
     logs \
     --selector=app.kubernetes.io/name=nvidia-device-plugin \
     --tail=300 \
     --prefix=true"

capture_remote \
  "node-gpu-resources.txt" \
  'printf "capacity="; \
   k3s kubectl get nodes \
     -o jsonpath="{.items[0].status.capacity.nvidia\.com/gpu}"; \
   printf "\nallocatable="; \
   k3s kubectl get nodes \
     -o jsonpath="{.items[0].status.allocatable.nvidia\.com/gpu}"; \
   printf "\n"'

capture_remote \
  "node-description.txt" \
  'k3s kubectl describe nodes'

capture_remote \
  "cluster-events.txt" \
  'k3s kubectl get events \
     --all-namespaces \
     --sort-by=.metadata.creationTimestamp'

# The validation playbook may leave the smoke Pod in place specifically so the
# wrapper can capture its logs. Missing smoke resources do not hide the primary
# validation result; their absence is recorded in the evidence file.
capture_remote \
  "smoke-workload.txt" \
  'if k3s kubectl \
        --namespace gpu-validation \
        get pod gpu-vectoradd >/dev/null 2>&1; then
       k3s kubectl \
         --namespace gpu-validation \
         get pod gpu-vectoradd \
         -o wide
       printf "\n--- describe ---\n"
       k3s kubectl \
         --namespace gpu-validation \
         describe pod gpu-vectoradd
       printf "\n--- logs ---\n"
       k3s kubectl \
         --namespace gpu-validation \
         logs pod/gpu-vectoradd
   else
       echo "gpu-validation/gpu-vectoradd is not present."
   fi'

EVIDENCE_CAPTURE_STATUS="pass"

CURRENT_STAGE="idempotency-check"

run_playbook \
  "${INSTALL_PLAYBOOK}" \
  "${RAW_DIR}/second-run.log"

if grep -Eq 'changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' \
  "${RAW_DIR}/second-run.log"; then
  IDEMPOTENCY_STATUS="pass"
else
  IDEMPOTENCY_STATUS="fail"
  fail "Second run was not idempotent; inspect ${RAW_DIR}/second-run.log."
fi

CURRENT_STAGE="finalize"

write_result "pass" "none" "${IDEMPOTENCY_STATUS}"
write_checksums

FINALIZED="true"
trap - ERR

printf '\nStep 1.5 completed successfully.\n'
printf 'Run ID: %s\n' "${RUN_ID}"
printf 'Evidence: %s\n' "${RUN_ROOT}"
printf 'Expected Kubernetes GPU capacity: %s\n' "${EXPECTED_GPU_COUNT}"
