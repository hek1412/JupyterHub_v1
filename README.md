# JupyterHub_v1
docker build -t jupyterlab-v2 -f Dockerfile.jupyterlab .
docker tag jupyterlab-v2  hek1412/dockerfile.jupyterlab_v2:latest 
docker push hek1412/dockerfile.jupyterlab_v2:latest
