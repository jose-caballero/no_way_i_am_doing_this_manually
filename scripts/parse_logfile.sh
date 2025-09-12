#!/bin/bash

# ============================================================================== 
#
# this script just parses the logfile from another script and grabs
# the most relevant paragraphs.
#
# First, it puts into a variable all paragraphs containing the string "fatal:"
# and prints out the content of this variable. 
# These are the paragraphs where Ansible reports a TASK failing. 
# The reason we use a variable instead of just printing directly the lines
# is because we need to make a decision later on about what return code this 
# script should return based on the presence or not of such paragraphs with 
# the string "fatal:".
#
# Second, it puts into another variable the summary report in the paragraph
# that starts with string "PLAY RECAP".
#
# Finally, we check if the variable where we stored the failure paragraphs is
# empty or not, and we return either 0 or 1 based on that.
#
# ============================================================================== 

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
