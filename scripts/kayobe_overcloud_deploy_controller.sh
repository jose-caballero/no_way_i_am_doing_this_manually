#!/bin/bash


current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILEDIR="${HOME}/hv_migration_scripts/logs"
mkdir -p $LOGFILEDIR
LOGFILE="${LOGFILEDIR}/logs_overcloud_deploy_controller_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe overcloud service deploy -kl controllers --limit controllers -kt common &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
