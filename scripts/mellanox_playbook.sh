#!/bin/bash

HYPERVISOR=$1

current_datetime=$(date +"%Y_%m_%d_%H_%M")
LOGFILE="logs.mallanox.${current_datetime}"

source ~/kayobe-prod/env-vars.sh
ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i ${HYPERVISOR}, --extra-vars "pxe_target=${HYPERVISOR}" &> $LOGFILE
cat $LOGFILE | awk -v RS= -v ORS="\n\n" '/^fatal/ { print; next } { last = $0 } END { print last }'

#
#  Explanation of the awk command:
#
#   - RS=                       treats paragraphs (blocks separated by blank lines) as records.
#   - ORS="\n\n"                ensures output paragraphs stay separated.
#   - /^fatal/ { print; next }  prints any paragraph starting with "fatal" immediately.
#   - { last = $0 }             saves each paragraph as the potential "last paragraph".
#   - END { print last }        prints the final paragraph after all input is read.
#
