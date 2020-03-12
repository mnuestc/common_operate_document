FROM ubuntu:16.04

RUN mkdir /root/.config\
    && mkdir /root/src\
    && mkdir /root/cfg

COPY pip.conf /root/.config/pip/
COPY sources.list /etc/apt/
COPY cfg /root/cfg

# RUN apt-get autoclean\
#     && apt-get update\    
#     && apt-get install -y --no-install-recommends\ 
#     install net-tools\
#     inetutils-ping\
#     nano\
#     build-essential\
#     python3-dev\ 
#     python3-numpy\     
#     python3-pip
RUN apt-get autoclean\
    && apt-get update\    
    && apt-get install -y --no-install-recommends\ 
    build-essential \
    python3-dev\ 
    python3-numpy\     
    python3-pip\
    nano


RUN pip3 install  --upgrade pip
RUN pip3 --no-cache-dir install setuptools   
RUN pip3 install setuptools --upgrade
RUN pip3 --no-cache-dir install flask\      
    requests\    
    pyyaml\
    kubernetes\ 
    grpcio\
    protobuf\
    grpcio-tools
    
# RUN pip3 install numpy --upgrade
RUN pip3 install py-radix --upgrade
RUN pip3 install IPy --upgrade  

EXPOSE 55666

COPY serviceMangerGrpc /root/serviceMangerGrpc
CMD ["python3","/root/serviceMangerGrpc/grpcManagerServer/k8sManager.py"]
