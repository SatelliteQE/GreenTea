FROM fedora:latest

# install packages
RUN yum install git python-virtualenv -y
RUN git clone https://github.com/SatelliteQE/GreenTea.git
RUN cat GreenTea/requirement-rpms.txt | xargs yum install git python-virtualenv -y python-devel postgresql-devel

# create user for service
RUN useradd -ms /bin/bash greentea
RUN chown -R greentea GreenTea 

USER greentea

RUN virtualenv GreenTea/env

RUN . GreenTea/env/bin/activate && pip install -r GreenTea/requirement.txt

# create default value for running service
RUN python -c 'import random; print "import os\nfrom basic import *\nSECRET_KEY=\"" + "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]) + "\"" ' > GreenTea/tttt/settings/production.py 

RUN cd GreenTea && . env/bin/activate && python manage.py syncdb --all || true
RUN cd GreenTea && . env/bin/activate && python manage.py migrate --fake

EXPOSE 8080

CMD cd GreenTea && . env/bin/activate && python manage.py runserver
