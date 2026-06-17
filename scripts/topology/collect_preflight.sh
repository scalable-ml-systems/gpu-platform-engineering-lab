#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="results/topology"
mkdir -p "${OUT_DIR}"

echo "[1/8] Capturing OS info..."
cat /etc/os-release | tee "${OUT_DIR}/os-release.txt"
uname -a | tee "${OUT_DIR}/uname.txt"

echo "[2/8] Capturing CPU info..."
lscpu | tee "${OUT_DIR}/lscpu.txt"

echo "[3/8] Capturing memory info..."
free -h | tee "${OUT_DIR}/free-h.txt"

echo "[4/8] Capturing NUMA info..."
numactl --hardware | tee "${OUT_DIR}/numactl-hardware.txt" || true

echo "[5/8] Capturing PCIe tree..."
lspci -tv | tee "${OUT_DIR}/lspci-tv.txt"

echo "[6/8] Capturing NVIDIA GPU state..."
nvidia-smi | tee "${OUT_DIR}/nvidia-smi.txt"

echo "[7/8] Capturing GPU list..."
nvidia-smi -L | tee "${OUT_DIR}/nvidia-smi-L.txt"

echo "[8/8] Capturing GPU topology matrix..."
nvidia-smi topo -m | tee "${OUT_DIR}/nvidia-smi-topo-m.txt"

echo "Preflight capture complete. Results saved to ${OUT_DIR}"
