#!/bin/bash
# author: Pavel Studenik
# email: pstudeni@redhat.com

/usr/bin/time -o result.txt -f "%e\n%x" $1
EXITCODE=$( cat result.txt | tail -n 1)
TIME=$( cat result.txt | head -n 1)
HOSTNAME="localhost:8000"

curl --data "label=$2&name=$3&description=$4&duration=$TIME&exitcode=$EXITCODE" "http://$HOSTNAME/api"
