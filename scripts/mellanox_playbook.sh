#!/bin/bash

source ~/kayobe-prod/env-vars.sh
ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i ${HYPERVISOR}, --extra-vars "pxe_target=${HYPERVISOR}"
