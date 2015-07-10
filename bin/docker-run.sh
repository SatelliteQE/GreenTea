#!/usr/bin/bash
# Author: Pavel Studeni <pstudeni@redhat.com>

# How often run script for pickup tasks in seconds
schedule_t=10 # 10s.
check_t=600 # 10min.


# For asynchronous operation Green Tea needs to run cron
# */1 * * * * 	greentea 	python /data/Greantea/manage.py pickup --traceback
function schedule {
    while true; do
	   python manage.py pickup -vvv
	   sleep $schedule_t
    done
}


# Following command check status of beaker jobs (automation tests)
# */20 * * * * 	greentea 	python /data/Greantea/manage.py check --quiet --traceback
function check {
    while true; do
	   python manage.py check -vv
	   sleep $check_t
    done
}

HOME=/data/GreenTea
source  $HOME/env/bin/activate
cd $HOME && \
    schedule & \
    check &
python $HOME/manage.py runserver 0.0.0.0:8000

