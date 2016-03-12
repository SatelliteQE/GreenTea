[![Build Status](https://travis-ci.org/SatelliteQE/GreenTea.svg?branch=master)](https://travis-ci.org/SatelliteQE/GreenTea)

# GreenTea

Green Tea is tools for automation testing (quality assurance). The service collects data from beaker's jobs, saves it to database and creates statistic for users.

Documentation you can find on project's [github wiki](https://github.com/SatelliteQE/GreenTea/wiki)

## Quick start guide

Easy way to run Green Tea is using docker https://registry.hub.docker.com/u/pajinek/greentea/

```
docker pull pajinek/greentea
docker run -i -t -p 80:8000 pajinek/greentea 
```

If you test project with gained systems from Beaker, then you must fill Beaker's authentication values.

```
docker pull pajinek/greentea
docker run -i -t -p 80:8000 \
  -e BEAKER_SERVER=<beaker_server> \
  -e BEAKER_USER=<beaker_user> \
  -e BEAKER_PASS=<beaker_pass> \
pajinek/greentea 
```

or

```
git clone https://github.com/SatelliteQE/GreenTea.git
cd GreenTea
sudo docker build -t greentea .
sudo docker run -i -t -p 80:8000 \
  -e BEAKER_SERVER=<beaker_server> \
  -e BEAKER_USER=<beaker_user> \
  -e BEAKER_PASS=<beaker_pass> \
greentea 
``` 

Service runs on default port 80 (link on your system is http://localhost/)

**login**: admin
**password**: pass

And system's root password is **GreenTea!**.

## How to start with Green Tea

Basic information for first use you can find on public wiki [wiki:start](https://github.com/SatelliteQE/GreenTea/wiki/Start)

## How to setup project

Information about setting you find on wiki page [wiki:setup](https://github.com/SatelliteQE/GreenTea/wiki/Setup)
