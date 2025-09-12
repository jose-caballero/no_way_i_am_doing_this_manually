#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="${HOME}/hv_migration_scripts/logs/logs_overcloud_deploy_hypervisor_${HYPERVISOR}_${current_datetime}"

source ~/kayobe-prod/env-vars.sh

kayobe overcloud service deploy -kl $HYPERVISOR --limit $HYPERVISOR &> $LOGFILE

echo "Relevant lines from the playbook output:"
#cat $LOGFILE | awk -v RS= -v ORS="\n\n" '/fatal:/ || /PLAY RECAP/'
FAILED_CONTENT=$(cat $LOGFILE | awk -v RS= -v ORS="\n\n" '/fatal:/')
echo "$FAILED_CONTENT"

echo ""
RECAP_CONTENT=$(cat $LOGFILE | awk -v RS= -v ORS="\n\n" '/PLAY RECAP/')
echo "$RECAP_CONTENT"

if [[ -n $FAILED_CONTENT ]]; then
        exit 1
else
        exit 0
fi

#
#  Explanation of the awk command:
#
#   - RS=                           treats paragraphs (blocks separated by blank lines) as records.
#   - ORS="\n\n"                    ensures output paragraphs stay separated.
#   - '/fatal:/ || /PLAY RECAP/'    prints any paragraph including strings "fatal:" or "PLAY RECAP"
