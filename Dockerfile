FROM centos:7

RUN mkdir -p /data/greentea /var/log/greentea
WORKDIR /data/greentea
ENV HOME /data/greentea
ADD requirement /data/greentea/requirement

RUN echo "root:GreenTea!" | chpasswd

# install packages
RUN curl https://beaker-project.org/yum/beaker-client-CentOS.repo -o /etc/yum.repos.d/beaker-client-CentOS.repo \
    && cat requirement/rpms-*.txt | xargs yum install -y \
    && yum clean all \
    && chmod 755 /data/ -R

ADD . /data/greentea/

# update CA certs
RUN ! [ -f $HOME/tttt/conf/*.crt ] || ( cp $HOME/tttt/conf/*.crt /etc/pki/ca-trust/source/anchors/ \
    && update-ca-trust extract )

# create enviroment
RUN useradd -ms /bin/bash greentea \
    && chown greentea:greentea -R /data/greentea /var/log/greentea

USER greentea
ENV DJANGO_SETTINGS_MODULE tttt.settings.production

RUN virtualenv $HOME/env \
    && cd $HOME \
    && . env/bin/activate \
    && pip install -r $HOME/requirement/requirement.txt \
    && pip install -r $HOME/requirement/requirement-postgresql.txt

# install cron and enable cron
# it doesn't use for docker, only for physical system
# RUN yum install crontabs -y && mv $HOME/tttt/conf/cron/greentea.cron /etc/cron.d/

COPY bin/docker-entrypoint.sh /usr/local/bin/

EXPOSE 8000
VOLUME ["/data/greentea/tttt/static", "/data/greentea/tttt/storage"]

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["greentea"]
