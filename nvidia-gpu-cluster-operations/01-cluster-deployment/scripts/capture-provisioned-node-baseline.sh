#!/usr/bin/env bash

set -uo pipefail

HARDWARE_PROFILE_ID="${HARDWARE_PROFILE_ID:-hw-rtx4090-4gpu-pcie-r01}"
EXPERIMENT_ID="${EXPERIMENT_ID:-exp-host-baseline-rtx4090-r01}"

EVIDENCE_ROOT="${EVIDENCE_ROOT:-01-cluster-deployment/evidence/${HARDWARE_PROFILE_ID}/${EXPERIMENT_ID}}"
RAW_DIR="${EVIDENCE_ROOT}/raw"

mkdir -p "${RAW_DIR}"

capture_command() {
    local artifact_name="$1"
    shift

    local command_text="$*"
    local output_file="${RAW_DIR}/${EXPERIMENT_ID}--${artifact_name}--raw.txt"

    {
        echo "# captured_at_utc: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo "# hostname: $(hostname)"
        echo "# command: ${command_text}"
        echo

        bash -lc "${command_text}"
        command_status=$?

        echo
        echo "# exit_code: ${command_status}"
    } >"${output_file}" 2>&1
}

capture_command "hostname" \
    "hostnamectl 2>/dev/null || hostname"

capture_command "operating-system" \
    "cat /etc/os-release"

capture_command "kernel" \
    "uname -a && printf '\nKernel release: ' && uname -r"

capture_command "virtualization" \
    "systemd-detect-virt 2>/dev/null || true"

capture_command "cpu-topology" \
    "lscpu"

capture_command "numa-topology" \
    "if command -v numactl >/dev/null 2>&1; then numactl --hardware; else echo 'numactl not installed'; fi"

capture_command "memory" \
    "free -b && printf '\n/proc/meminfo:\n' && cat /proc/meminfo"

capture_command "storage" \
    "lsblk -b -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL && printf '\nFilesystems:\n' && df -B1 -T"

capture_command "network-interfaces" \
    "ip -details -brief link && printf '\nAddresses:\n' && ip -brief address"

capture_command "network-routes" \
    "ip route show table all"

capture_command "gpu-list" \
    "nvidia-smi -L"

capture_command "gpu-inventory" \
    "nvidia-smi --query-gpu=index,uuid,name,memory.total,pci.bus_id,driver_version,pstate,temperature.gpu,power.limit --format=csv,noheader"

capture_command "nvidia-driver" \
    "cat /proc/driver/nvidia/version 2>/dev/null || true"

capture_command "nvidia-devices" \
    "ls -la /dev/nvidia* 2>/dev/null || true"

capture_command "loaded-nvidia-modules" \
    "lsmod | grep -E '^nvidia|^nouveau' || true"

capture_command "container-runtime-inventory" \
    "command -v docker || true; command -v containerd || true; command -v ctr || true; command -v crictl || true; command -v nvidia-ctk || true"

capture_command "time-state" \
    "date -u && timedatectl 2>/dev/null || true"

capture_command "git-state" \
    "git rev-parse HEAD && git branch --show-current && git status --short"

echo "Baseline capture complete:"
echo "${EVIDENCE_ROOT}"
