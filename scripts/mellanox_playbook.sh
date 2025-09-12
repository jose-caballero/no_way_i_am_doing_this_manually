#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="${HOME}/hv_migration_scripts/logs/logs_mellanox_${HYPERVISOR}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i ${HYPERVISOR}, --extra-vars "pxe_target=${HYPERVISOR}" &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
