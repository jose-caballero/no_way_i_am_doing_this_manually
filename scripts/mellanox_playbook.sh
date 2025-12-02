#!/bin/bash

# 
# convert the list of hypervisor names passed as inputs
# into 2 variables:
#   - the hostnames split by comma
#   - the hostnames split by colon
#   - the hostnames split by underscore
#
HYPERVISORS=$@
HYPERVISORS_COMMA=""
HYPERVISORS_COLON=""
HYPERVISORS_UNDER=""
for HV in $HYPERVISORS; do
    if [ -z "${HYPERVISORS_COMMA}" ]; then
        HYPERVISORS_COMMA="$HV"
    else
        HYPERVISORS_COMMA="${HYPERVISORS_COMMA},$HV"
    fi
    if [ -z "${HYPERVISORS_COLON}" ]; then
        HYPERVISORS_COLON="$HV"
    else
        HYPERVISORS_COLON="${HYPERVISORS_COLON}:$HV"
    fi
    if [ -z "${HYPERVISORS_UNDER}" ]; then
        HYPERVISORS_UNDER="$HV"
    else
        HYPERVISORS_UNDER="${HYPERVISORS_UNDER}_$HV"
    fi
done

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILEDIR="${HOME}/hv_migration_scripts/logs"
mkdir -p $LOGFILEDIR
LOGFILE="${LOGFILEDIR}/logs_mellanox_${HYPERVISORS_UNDER}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i ${HYPERVISORS_COMMA}, --extra-vars "pxe_target=${HYPERVISORS_COLON}" &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
