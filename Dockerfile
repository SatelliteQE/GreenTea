FROM fedora:latest

WORKDIR /data/

# install packages
RUN yum install git -y
RUN git clone https://github.com/SatelliteQE/GreenTea.git
RUN cat GreenTea/requirement/rpms-*.txt | xargs yum install -y
RUN chmod 755 /data/ -R

# create enviroment
RUN useradd -ms /bin/bash greentea
RUN chown greentea:greentea -R GreenTea

USER greentea
ENV HOME /data/GreenTea

RUN virtualenv $HOME/env
RUN . $HOME/env/bin/activate && pip install -r $HOME/requirement/requirement.txt

# create default value for running service
RUN python -c 'import random; print "import os\nfrom basic import *\nDEBUG=True\nSECRET_KEY=\"" + "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]) + "\"" ' > GreenTea/tttt/settings/production.py 

RUN mkdir -p $HOME/tttt/static

RUN . $HOME/env/bin/activate && \
    python $HOME/manage.py syncdb --all || true && \
    python $HOME/manage.py migrate --fake
    python $HOME/manage.py collectstatic -c --noinput

EXPOSE 8000
CMD . $HOME/env/bin/activate && python $HOME/manage.py runserver 0.0.0.0:8000
