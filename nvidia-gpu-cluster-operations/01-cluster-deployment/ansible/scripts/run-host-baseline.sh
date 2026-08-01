#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

if [[ ! -f inventory/hosts.yaml ]]; then
  echo "ERROR: inventory/hosts.yaml does not exist."
  echo "Copy inventory/hosts.example.yaml and update the SSH values."
  exit 1
fi

ansible-playbook playbooks/host-baseline.yaml
ansible-playbook playbooks/validate-host-baseline.yaml
