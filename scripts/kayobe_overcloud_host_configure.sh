#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="${HOME}/hv_migration_scripts/logs/logs_overcloud_host_configure_${HYPERVISOR}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe overcloud host configure -e selinux_do_reboot=true -kl $HYPERVISOR --limit $HYPERVISOR &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
