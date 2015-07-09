FROM fedora:latest

WORKDIR /data/

# install packages
RUN yum install git wget -y \
    && wget https://beaker-project.org/yum/beaker-client-Fedora.repo -O /etc/yum.repos.d/beaker-client-Fedora.repo \
    && git clone https://github.com/SatelliteQE/GreenTea.git \
    && cat GreenTea/requirement/rpms-*.txt | xargs yum install -y \
    && chmod 755 /data/ -R

# create enviroment
RUN useradd -ms /bin/bash greentea \
    && chown greentea:greentea -R GreenTea

USER greentea
ENV HOME /data/GreenTea

RUN virtualenv $HOME/env \
    && . $HOME/env/bin/activate \
    && pip install -r $HOME/requirement/requirement.txt

# create default value for running service
RUN python -c 'import random; print "import os\nfrom basic import *\nDEBUG=True\nSECRET_KEY=\"" + "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]) + "\"" ' > GreenTea/tttt/settings/production.py 

RUN mkdir -p $HOME/tttt/static \
    && . $HOME/env/bin/activate \
    && python $HOME/manage.py syncdb --all || true \
    && python $HOME/manage.py migrate --fake \
    && python $HOME/manage.py collectstatic -c --noinput

# create first user
RUN . $HOME/env/bin/activate && \
    echo 'from django.contrib.sites.models import Site; site = Site.objects.create(domain="localhost", name="localhost"); site.save()' | python $HOME/manage.py shell && \
    echo 'from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@example.com", "pass")' | python $HOME/manage.py shell

# install cron and enable cron
# it doesn't use for docker, only for real system
# RUN yum install crontabs -y && mv $HOME/tttt/conf/cron/greentea.cron /etc/cron.d/

USER greentea

EXPOSE 8000
CMD . $HOME/bin/docker-run.sh
