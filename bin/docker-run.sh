#!/usr/bin/bash
# author: Pavel Studeni <pstudeni@redhat.com>

# how often run script for pickup tasks
timeout=10

function schedule {
    while true; do
	   python ../manage.py pickup -vvv
	   sleep $timeout
    done
}

source  ../env/bin/activate
schedule &
python ../manage.py runserver 0.0.0.0:8000

