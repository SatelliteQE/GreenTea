FROM centos:7

RUN mkdir -p /data/greentea
WORKDIR /data/greentea
ADD requirement /data/greentea/requirement

RUN echo "root:GreenTea!" | chpasswd

# install packages
RUN curl https://beaker-project.org/yum/beaker-client-CentOS.repo -o /etc/yum.repos.d/beaker-client-CentOS.repo \
    && cat requirement/rpms-*.txt | xargs yum install -y \
    && yum clean all \
    && chmod 755 /data/ -R

ADD . /data/greentea/

# create enviroment
RUN useradd -ms /bin/bash greentea \
    && chown greentea:greentea -R /data/greentea

USER greentea
ENV HOME /data/greentea
ENV DJANGO_SETTINGS_MODULE tttt.settings.production

RUN virtualenv $HOME/env \
    && cd $HOME \
    && . env/bin/activate \
    && pip install -r $HOME/requirement/requirement.txt

# create default values for running service
RUN sh $HOME/bin/init-secretkey.sh > $HOME/tttt/settings/production.py \
    && echo "ALLOWED_HOSTS=['*']" >> $HOME/tttt/settings/production.py \
    && mkdir -p $HOME/tttt/static $HOME/storage

# install cron and enable cron
# it doesn't use for docker, only for real system
# RUN yum install crontabs -y && mv $HOME/tttt/conf/cron/greentea.cron /etc/cron.d/

EXPOSE 8000
VOLUME /data/greentea/tttt/static

CMD sh $HOME/bin/docker-run.sh
