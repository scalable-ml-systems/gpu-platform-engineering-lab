#!/usr/bin/env bash

set -uo pipefail

HARDWARE_PROFILE_ID="${HARDWARE_PROFILE_ID:-hw-rtx4090-4gpu-pcie-r01}"
EXPERIMENT_ID="${EXPERIMENT_ID:-exp-nvidia-host-validation-rtx4090-r01}"

EVIDENCE_ROOT="${EVIDENCE_ROOT:-01-cluster-deployment/evidence/${HARDWARE_PROFILE_ID}/${EXPERIMENT_ID}}"
RAW_DIR="${EVIDENCE_ROOT}/raw"

mkdir -p "${RAW_DIR}"

capture() {
    local artifact="$1"
    shift

    local command_text="$*"
    local output_file="${RAW_DIR}/${EXPERIMENT_ID}--${artifact}--raw.txt"

    {
        echo "# captured_at_utc: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo "# hostname: $(hostname)"
        echo "# command: ${command_text}"
        echo

        bash -lc "${command_text}"
        exit_code=$?

        echo
        echo "# exit_code: ${exit_code}"
    } >"${output_file}" 2>&1
}

capture "nvidia-smi" \
    "nvidia-smi"

capture "gpu-list" \
    "nvidia-smi -L"

capture "gpu-inventory" \
    "nvidia-smi \
      --query-gpu=index,uuid,name,driver_version,memory.total,pci.bus_id,compute_mode,persistence_mode,pstate,temperature.gpu,power.draw,power.limit \
      --format=csv,noheader"

capture "driver-version" \
    "cat /proc/driver/nvidia/version"

capture "kernel-modules" \
    "lsmod | grep -E '^nvidia|^nouveau' || true"

capture "nvidia-module-details" \
    "modinfo nvidia 2>/dev/null | grep -E '^(filename|version|vermagic):' || true"

capture "device-files" \
    "ls -la /dev/nvidia* 2>/dev/null || true"

capture "gpu-health-query" \
    "nvidia-smi -q"

capture "kernel-driver-events" \
    "sudo dmesg -T | grep -iE 'NVRM|Xid|fallen off|nvidia|nouveau' || true"

capture "nvidia-packages" \
    "dpkg-query -W -f='\${Package}\t\${Version}\n' 2>/dev/null \
      | grep -E '^(nvidia|libnvidia|cuda|containerd|docker)' \
      | sort || true"

capture "nvidia-tooling" \
    "command -v nvidia-smi || true
     command -v nvidia-ctk || true
     command -v nvcc || true
     command -v containerd || true
     command -v docker || true"

echo "NVIDIA host validation evidence captured:"
echo "${EVIDENCE_ROOT}"
