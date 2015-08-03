# GreenTea


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

## How to 

Basic information for first use you can find on public wiki [wiki:start](https://github.com/SatelliteQE/GreenTea/wiki/Start)

## Setup

Information about setting you find on wiki page [wiki:setup](https://github.com/SatelliteQE/GreenTea/wiki/Setup)
