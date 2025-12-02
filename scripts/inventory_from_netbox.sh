#!/bin/bash

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILEDIR="${HOME}/hv_migration_scripts/logs"
mkdir -p $LOGFILEDIR
LOGFILE="${LOGFILEDIR}/logs_inventory_netbox_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe playbook run ansible/build-inventory-from-netbox.yml &> $LOGFILE

${HOME}/hv_migration_scripts/parse_logfile.sh $LOGFILE
exit $?
