#!/usr/bin/python
# author: Pavel Studenik


from fabric import tasks
from fabric.api import env, get, local, run
from fabric.context_managers import cd
from fabric.network import disconnect_all

env.hosts = [
    ""
]

HOME_PATH = ""


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


def deploy():
    with cd("%s" % HOME_PATH):
        run("svn update")
        run("source env/bin/activate && python manage.py collectstatic --noinput")
        run("uwsgi-manager -R 1")

def db_backup():
    backup_file = "/tmp/tttt.backup.gz"
    run("export PGPASSWORD="" pg_dump tttt -U tttt_user -h localhost | gzip > %s" % backup_file)
    get("%s %s" % (backup_file, backup_file))

def download():
    get("%s/db.sqlite3" % HOME_PATH, "db.sqlite3")


def main():
    pass

if __name__ == '__main__':
    main()
