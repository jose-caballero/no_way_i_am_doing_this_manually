#!/bin/bash

# Check if hostname parameter is provided
if [ $# -eq 0 ]; then
    echo "Error: No hostname provided"
    echo "Usage: $0 <hostname>"
    exit 1
fi

# Set SCRIPTHOST from the first parameter
SCRIPTHOST=$1
FILE=${SCRIPTHOST}_old.txt

aq show host --hostname $SCRIPTHOST >> $FILE
SYSTEMID=$(aq show host --hostname $SCRIPTHOST | grep system | sed -n "s/Machine: \(.*\)$/\1/p")
VLAN_NAME=$(aq show host --hostname $SCRIPTHOST | grep "Interface: vlan" | cut -d ' ' -f 4)
VLAN_MAC_ADDRESS=$(aq show host --hostname $SCRIPTHOST | grep "Interface: vlan" | cut -d ' ' -f 5)
VLAN_IP_ADDRESS=$(aq show host --hostname $SCRIPTHOST | grep "Provides: " | grep vlan | cut -d '[' -f 2 | tr -d '[]')

aq del_host --hostname $SCRIPTHOST

if grep -q "Interface: br0" $FILE; then
    aq del_interface --machine $SYSTEMID --interface br0
fi

if grep -q "Interface: eth0" $FILE; then
    aq del_interface --machine $SYSTEMID --interface eth0
fi

aq del_interface_address --machine $SYSTEMID --ip "${VLAN_IP_ADDRESS}" --interface $VLAN_NAME
aq del_interface --mac "${VLAN_MAC_ADDRESS}"

if grep -q "Interface: bmc" $FILE; then
    # Extract Network Environment
    NET_ENV=$(grep -A3 "Interface: bmc" "$FILE" | grep "Network Environment:" | sed 's/.*Network Environment: //')

    # Extract IP address - looks for the IP in square brackets
    IP=$(grep -A4 "Interface: bmc" "$FILE" | grep "Provides:" | grep -o '\[.*\]' | tr -d '[]')

    aq del_interface_address --machine $SYSTEMID --ip $IP --interface bmc0 --network_environment $NET_ENV
fi

aq del_machine --machine $SYSTEMID
echo "Machine deleted..."

echo "Importing ${SCRIPTHOST}"
netbox2aquilon --hostname $SCRIPTHOST --archetype cloud --domain prod_cloud prod --osname rocky --osversion 9x-x86_64
aq update_interface --hostname $SCRIPTHOST --interface eth0 --boot --default_route
