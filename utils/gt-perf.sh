#!/bin/bash
# author: Pavel Studenik
# email: pstudeni@redhat.com

# using:
# python gt-perf.sh '$COMMAND' '$TAG' '$TITLE' '$DESCRIPTION'

# for example:
# python gt-perf.sh 'sleep 2' 'tag-sleep' 'sleep 2 sec' 'Script tests how long actually waits script sleep.'

/usr/bin/time -o result.txt -f "%e\n%x" $1
EXITCODE=$( cat result.txt | tail -n 1)
TIME=$( cat result.txt | head -n 1)
HOSTNAME="localhost:8000"

curl --data "label=$2&name=$3&description=$4&duration=$TIME&exitcode=$EXITCODE" "http://$HOSTNAME/api"
