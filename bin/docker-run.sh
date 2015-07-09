#!/usr/bin/bash
# author: Pavel Studeni <pstudeni@redhat.com>

# how often run script for pickup tasks
timeout=10

function schedule {
    while true; do
	   python manage.py pickup -vvv
	   sleep $timeout
    done
}

HOME=/data/GreenTea
source  $HOME/env/bin/activate
cd $HOME && schedule &
python $HOME/manage.py runserver 0.0.0.0:8000

