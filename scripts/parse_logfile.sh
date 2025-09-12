#!/bin/bash

LOGFILE=$1

echo ""
echo "The full path to the logfile is $LOGFILE"
echo "Here are the most relevant paragraphs from the logfile:"
echo ""

FAILED_CONTENT=$(awk -v RS= -v ORS="\n\n" '/fatal:/' $LOGFILE)
echo "$FAILED_CONTENT"

echo ""
RECAP_CONTENT=$(awk -v RS= -v ORS="\n\n" '/PLAY RECAP/' $LOGFILE)
echo "$RECAP_CONTENT"

if [[ -n $FAILED_CONTENT ]]; then
	exit 1
else
	exit 0
fi


#
#  Explanation of the awk commands:
#
#   - RS=               treats paragraphs (blocks separated by blank lines) as records.
#   - ORS="\n\n"        ensures output paragraphs stay separated.
#   - '/fatal:/'    	prints any paragraph including strings "fatal:" or "PLAY RECAP"
#   - '/PLAY RECAP/'    prints any paragraph including strings "fatal:" or "PLAY RECAP"
#
