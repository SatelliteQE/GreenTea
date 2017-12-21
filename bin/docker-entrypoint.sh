#!/bin/bash
# Author: Pavel Studeni <pstudeni@redhat.com>

# How often run script for pickup tasks in seconds
schedule_t=30 # 30s.
check_t=600 # 10min.

# For asynchronous operation Green Tea needs to run cron
# */1 * * * * 	greentea 	python /data/Greantea/manage.py pickup --traceback
function schedule {
    echo "service schedule run ..."
    while true; do
        python manage.py pickup
        sleep $schedule_t
    done
}


# Following command check status of beaker jobs (automation tests)
# */20 * * * * 	greentea 	python /data/Greantea/manage.py check --quiet --traceback
function check {
    echo "service check run ..."
    while true; do
        python manage.py check_beaker
        sleep $check_t
    done
}

function manage() {
    echo "$1" | python $HOME/manage.py shell
}

HOME=/data/greentea
chown greentea:greentea -R $HOME
source $HOME/env/bin/activate && cd $HOME

# Set postgresql

if ! [ -z $POSTGRES_SERVER ]; then
    pip install -r $HOME/requirement/requirement-postgresql.txt

    # create postgres db and user for greentea
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -U postgres <<EOF
        CREATE USER tttt_user WITH PASSWORD '$POSTGRES_PASSWORD';
        CREATE DATABASE tttt owner tttt_user;
        ALTER USER tttt_user CREATEDB;
EOF

    # switch database to postgres
    echo "
DEBUG=False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tttt',
        'USER': 'tttt_user',
        'PASSWORD': '$POSTGRES_PASSWORD',
        'HOST': '$POSTGRES_SERVER',
        'PORT': '',
    }
}
" >> tttt/settings/production.py
fi

# Set local settings for running instance
# Beaker's variables
echo "BEAKER_SERVER=\"$BEAKER_SERVER\"" >> $HOME/tttt/settings/production.py
echo "BEAKER_OWNER=\"$BEAKER_USER\"" >> $HOME/tttt/settings/production.py
echo "BEAKER_PASS=\"$BEAKER_PASS\"" >> $HOME/tttt/settings/production.py

python $HOME/manage.py migrate --noinput

manage 'from django.contrib.sites.models import Site; site = Site.objects.create(domain="localhost", name="localhost"); site.save()'
manage 'from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@example.com", "pass")'

python $HOME/manage.py collectstatic -c --noinput

python manage.py check_beaker

# Run all services of Green Tea
schedule & # Schedule jobs
check & # Check all running jobs

# Run main web service
uwsgi --http :8000 --thunder-lock --enable-threads --wsgi-file tttt/wsgi.py

