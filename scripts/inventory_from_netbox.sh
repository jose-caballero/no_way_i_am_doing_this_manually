#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="${HOME}/logs/logs_inventory_netbox_${HYPERVISOR}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe playbook run ansible/build-inventory-from-netbox.yml &> $LOGFILE
cat $LOGFILE | awk -v RS= -v ORS="\n\n" '/fatal:/ || /PLAY RECAP/'

#
#  Explanation of the awk command:
#
#   - RS=                           treats paragraphs (blocks separated by blank lines) as records.
#   - ORS="\n\n"                    ensures output paragraphs stay separated.
#   - '/fatal:/ || /PLAY RECAP/'    prints any paragraph including strings "fatal:" or "PLAY RECAP"
