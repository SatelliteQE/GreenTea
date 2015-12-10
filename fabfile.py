#!/usr/bin/python
# author: Pavel Studenik

from fabric.api import env, get, local, run, sudo
from fabric.context_managers import cd

env.hosts = [""]

HOME_PATH = "/data/greentea/web"

def devel():
    env.hosts = "localhost"

def prod():
    env.hosts = "root@tttt.eng.rdu2.redhat.com"

def trans():
    local("svn update || git pull")
    local("source env/bin/activate")
    local("python manage.py makemessages -a -i \"env/*\"")
    local("python manage.py compilemessages")
    local("svn diff")


def verify():
    local("find ./ -not -path \"./env/*\" -name \"*.py\" | xargs isort")
    local(
        "find ./ -not -path \"./env/*\" -name \"*.py\" | xargs autopep8 -i --aggressive")
    local("python manage.py graph_models -a -g -o doc/images/erdiagram.png")

def stop():
    with cd("%s" % HOME_PATH):
        run("ls -l ../tttt.pid")
        run("uwsgi --stop ../tttt.pid")

def start():
    with cd("%s" % HOME_PATH):
        run("uwsgi tttt/conf/config.xml")
        run("ps aux | grep uwsgi")

def deploy():
    with cd("%s" % HOME_PATH):
        run("chown greentea:greentea . -R")
        sudo("git diff", user="greentea")
        sudo("git reset --hard", user="greentea")
        sudo("git pull", user="greentea")
        sudo("source env/bin/activate && python manage.py collectstatic --noinput", user="greentea")
        stop()
        start()


def db_backup():
    backup_file = "/tmp/tttt.backup.gz"
    run("export PGPASSWORD='' "
        "pg_dump tttt -U tttt_user -h localhost | gzip > %s" % backup_file)
    get("%s %s" % (backup_file, backup_file))

def db_restore(db_file):
    local("echo 'DROP DATABASE tttt; CREATE DATABASE tttt;' | psql -h localhost -U postgres")
    local("gunzip -c %s | psql -h localhost -U tttt_user tttt" % db_file)

def download():
    get("%s/db.sqlite3" % HOME_PATH, "db.sqlite3")


def main():
    pass


if __name__ == '__main__':
    main()
