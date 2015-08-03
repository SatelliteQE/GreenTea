# GreenTea


## Quick start guide

Easy way to run Green Tea is using docker https://registry.hub.docker.com/u/pajinek/greentea/

```
docker pull pajinek/greentea
docker run -i -t -p 80:8000 pajinek/greentea 
```
or

```
git clone https://github.com/SatelliteQE/GreenTea.git
cd GreenTea
sudo docker build -t greentea .
sudo docker run -i -t -p 80:8000 greentea 
``` 

Service runs on default port 80 (link on your system is http://localhost/)

**login**: admin
**password**: pass

And system's root password is **GreenTea!**.

## Setup

Information about setting you find on wiki page https://github.com/SatelliteQE/GreenTea/wiki/Setup
