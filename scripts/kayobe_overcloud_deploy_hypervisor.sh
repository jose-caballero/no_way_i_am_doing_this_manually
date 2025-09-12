#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="${HOME}/hv_migration_scripts/logs/logs_overcloud_deploy_hypervisor_${HYPERVISOR}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe overcloud service deploy -kl $HYPERVISOR --limit $HYPERVISOR &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
