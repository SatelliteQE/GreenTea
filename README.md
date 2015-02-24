# GreenTea


## How to install

Easy way to run Green Tea is using docker https://registry.hub.docker.com/u/pajinek/greentea/

```
docker pull pajinek/greentea
docker run -i -t -p 80:8000 pajinek/greentea 
```
or

```
git clone https://github.com/SatelliteQE/GreenTea.git
cd GreenTea
sudo docker build  -t --nocache greentea . 
sudo docker run -i -t -p 80:8000 greentea 
``` 
Service runs on port 80, you can go to link http://localhost/
