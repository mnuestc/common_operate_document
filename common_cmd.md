# 1.常用操作 

## 1.1 系统
uname -a               # 查看内核/操作系统/CPU信息
head -n 1 /etc/issue   # 查看操作系统版本
cat /proc/cpuinfo      # 查看CPU信息
hostname               # 查看计算机名
lspci -tv              # 列出所有PCI设备
lsusb -tv              # 列出所有USB设备
lsmod                  # 列出加载的内核模块
env                    # 查看环境变量

## 1.2 资源
free -m                # 查看内存使用量和交换区使用量
df -h                  # 查看各分区使用情况
du -sh <目录名>         # 查看指定目录的大小
grep MemTotal /proc/meminfo             # 查看内存总量
grep MemFree /proc/meminfo              # 查看空闲内存量
uptime                 # 查看系统运行时间、用户数、负载
cat /proc/loadavg      # 查看系统负载

## 1.3 磁盘和分区
mount | column -t      # 查看挂接的分区状态
fdisk -l               # 查看所有分区
swapon -s              # 查看所有交换分区
hdparm -i /dev/hda     # 查看磁盘参数(仅适用于IDE设备)
dmesg | grep IDE       # 查看启动时IDE设备检测状况

## 1.4 网络
ifconfig ： 查看与临时配置网络
ifdown 网卡设备名 ： 关闭网卡
ifup 网卡设备名 ： 启用网卡
netstat 网络状态查询
netstat -lntp          # 查看所有监听端口
netstat -antp          # 查看所有已经建立的连接
netstat -s             # 查看网络统计信息
netstat -tuln | grep LISTEN | wc l     #组合命令，查看系统中正在监听的端口数量：
-t 列出TCP协议端口
-u 列出UDP协议端口
-n 不适用域名与服务名，而是用ip地址和端口号
-l 仅列出在监听端口
-a 所有的连接
-r 路由表
traceroute IP
tracert ip
netstat -nupl (UDP类型的端口)
netstat -ntpl (TCP类型的端口)
telnet ip  端口号            #测试远程主机端口是否打开
iptables -L                 # 查看防火墙设置
route -n                    # 查看路由表
sudo ufw allow 8080         # 查看防火墙：默认情况下，Jenkins在端口8080上运行，所以让我们使用ufw打开该端口
sudo ufw status             # 检查ufw的状态以确认新规则
tunctl -d <虚拟网卡名>        # 刪除虚拟网卡
ifconfig <网桥名> down       # 刪除虚拟网桥
brctl delbr <网桥名>

将网卡tap0, eth0 移出bridge(br0)
brctl delif br0 tap0
brctl delif br0 eth0
常用的组合： 
- an 所有的连接和端口 
- tuln 查看正在监听TCP（t）和UDP（u）的端口 
- rn 查看网关 route -n

## 1.5 进程
ps -ef                          # 查看所有进程
top                             # 实时显示进程状态
## 1.6 用户
w                               # 查看活动用户
id <用户名>                      # 查看指定用户信息
last                            # 查看用户登录日志
cut -d: -f1 /etc/passwd         # 查看系统所有用户
cut -d: -f1 /etc/group          # 查看系统所有组
crontab -l                      # 查看当前用户的计划任务
## 1.7 服务
chkconfig --list                # 列出所有系统服务
chkconfig --list | grep on      # 列出所有启动的系统服务
## 1.8 程序
rpm -qa                         # 查看所有安装的软件包



# 2.实地部署

## 2.1 常用操作

sudo code . --user-data-dir="~/.vscode-root"
pip install -r requirement.txt

mkdir -p /etc/ansible && cp r ./ansible/* /etc/ansible
zip -r images.zip images
CA目录：/etc/kubernetes/ssl#

#java安装
sudo apt --fix-broken install
sudo apt-get install openjdk-8-jdk
java -version

chmod +x ./save.sh
sudo lsb_release a
sudo dpkg -l code
sudo dpkg -r code


谷歌安装
1.在终端中，输入以下命令：
sudo wget http://www.linuxidc.com/files/repo/google-chrome.list -P /etc/apt/sources.list.d/
将下载源加入到系统的源列表。

2.在终端中，输入以下命令：
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
导入谷歌软件的公钥，用于下面步骤中对下载软件进行验证。

3.在终端中，输入以下命令：
sudo apt-get update
用于对当前系统的可用更新列表进行更新。

4.在终端中，输入以下命令：
sudo apt-get install google-chrome-stable
google-chrome





# 3.虚拟机技术

## 3.1 虚拟化支持检测
find /dir -name filename
grep vmx /proc/cpuinfo
grep flags /proc/cpuinfo
cat /proc/cpuinfo greo|falgs
Libvirt/virsh
Libvirt，xml格式的配置文件在/etc/libvirt/qemu

qemu-img info controller-node.img
qemu-img resize controller-node.img +80G
qemu-img create -f qcow2 test01_add.qcow2 2G 
qemu-img info /home/data/iso/sys.qcow2                                  # 查询磁盘信息
qemu-img resize /home/data/iso/sys.qcow2 +50G                           # 增加50G空间
cp  /home/data/iso/sys.qcow2  /home/data/iso/sys-orig.qcow2             # 准备使用virt-resize调整分区空间，而virt-resize不能原地扩容，需要制作一个备份
virt-resize --expand /dev/sda1  /home/data/iso/sys-orig.qcow2  /home/data/iso/sys.qcow2     # 扩容分区/dev/sda1，这里可以扩容该磁盘的特定分区，最好确认需要扩容的挂载点所在分区，可以使用后面的验证分区大小命令确认需要扩容的分区

qemu-img info /home/data/iso/sys.qcow2      # 查看分区信息
virt-filesystems --long -h --all -a /home/data/iso/sys.qcow2            # 验证分区大小

## 3.2 Vagrant/virtualbox 磁盘扩容

vagrant halt <machine_name>     # 停止虚拟机

vboxmanage showhdinfo box-disk1.vmdk                                    # 进入VirtualBox VMs目录，查看并记录原磁盘uuid，留作后用
vboxmanage clonehd box-disk1.vmdk new-virtualdisk.vdi --format vdi      # 克隆磁盘，vmdk格式无法调整大小，需要转成vdi格式
vboxmanage modifyhd new-virtualdisk.vdi --resize 409600                 # 调整克隆磁盘的大小，这里调整为400G
vboxmanage clonehd new-virtualdisk.vdi resized.vmdk --format vmdk       # 在克隆磁盘的基础上再克隆vdi格式的磁盘
mv resized.vmdk box-disk1.vmdk                                          # 覆盖原磁盘（如果担心磁盘数据出现不可逆损坏，请先做好备份）
rm new-virtualdisk.vdi                                                  # 此时节已删除中间文件
vboxmanage internalcommands sethduuid box-disk1.vmdk <old_uuid>         # !!!此时启动虚机或查看磁盘信息会报错，提示uuid不匹配，因为磁盘已经变了，需要改回之前记录的uuid
vagrant up <machine_name>                                               # done，可以重启虚机了，可根据需要在虚机上进行磁盘分配，这里不再展开

# 4.DevOps

技术栈：
容器：docker
分布式基础设施：k8s
镜像库：harbor
代码仓库：gitlab
CI/CD工具：Jenkins



# 4.1docker

Docker常用启动命令
1.启动 ：systemctl start docker
2.守护进程重启：sudo systemctl daemon-reload
3.重启docker服务：systemctl restart docker
4.重启docker服务：sudo service docker restart
5.关闭：docker service docker stop   
6.关闭：docker systemctl stop docker
docker stop $(docker ps -aq)
docker rm -f $(docker ps -aq)

docker image ls
1.查看本地镜像：docker images
2.删除本地镜像：docker rmi 本地镜像id
3.列出所有容器：docker ps -a
4.停止容器运行：docker stop 容器id
5.删除容器：docker rm 容器id
6.进入容器：docker exec -it 容器id bash
7.实时动态查看容器最后n行日志：docker logs -f -t --tail n 容器id
8.查看容器挂载路径：docker inspect --format {{.Config.Volumes}}" 容器id

docker stop $(docker ps -aq)
docker rm -f $(docker ps -aq)


http://10.153.3.130:8080
curl X GET http:// 10.114.134.52:6060/v2/_catalog
result=$(curl http:// 10.114.134.52:6060/v2/_catalog)
result=$(curl http://10.114.201.35 /v2/_catalog) 
echo $result | jq .
若要保存为文件名：abc.json，在终端输入以下命令
echo $result | jq .　> abc.jsonDocker:

curl X GET http:// 10.114.134.52:6060/v2/_catalog
docker pull 192.168.0.107:6060/h3c/gaea-user-dashboard
docker pull 192.168.0.107:6060/h3c/gaea-operator-dashboard 

result=$( curl X GET http:// 10.114.134.52:6060/v2/_catalog) 
echo $result | jq 

若要保存为文件名：abc.json，在终端输入以下命令
echo $result | jq .　> abc.json


Make docker
Make start
docker pull 10.114.134.52:6060/mongo:3.4.10
Docker images 
Docker tag…
Make start

curl -XGEThttp:// 10.114.134.52:6060/
curl X GET http:// 10.114.134.52:6060/v2/_catalog
cat /etc/kubernetes/ssl/server.key
cat /etc/kubernetes/ssl/ca.crt cat /etc/kubernetes/ssl/ca.crt
kubectl get pod --all-namespaces
kubectl describe pod  peer0-org1-66b4f444d8-qxs4l -n net
path=%path%; D:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
sudo tar xzf Python-3.6.8.tgz
cd Python-3.6.8
sudo ./configure --enable-optimizations
sudo make altinstall

docker cp 315bc1299a02:/root /root /gaea-platform/mounted/operator-dashboard/
docker cp 315bc1299a02:/root /root /gaea-platform/mounted/user-dashboard/root
docker logs --tail 10 0f403e506587
docker-compose up -d
docker run -it --privileged=true -v /root/gaea-platform/mounted/user-dashboard:/var/www/app h3c/gaea-user-dashboard /bin/bash
docker exec -it a8f19dabdc9e /bin/bash
docker inspect container_name | grep Mounts -A 30

Docker镜像加速
# 新建 daemon.json 文件
$ sudo vim /etc/docker/daemon.json
{
    "registry-mirrors": ["http://hub-mirror.c.163.com"]
}

创建数据卷
docker volume create my-vol
数据卷列表
docker volume ls
查看数据卷具体信息
docker volume inspect my-vo


## 4.2 K8S

kubectl get nodes
kubectl get pod --all-namespaces
describe pod  peer0-org1-66b4f444d8-qxs4l -n net
cat /etc/kubernetes/ssl/ca.crt cat /etc/kubernetes/ssl/ca.crt 

kubectl get svc --all-namespaces
kubectl get pod --all-namespaces -o wide
kubectl get pod peer0-morg1-7886d746ff-pzbmb --namespace=mnet1
kubectl describe pods peer0-morg1-7886d746ff-pzbmb --namespace=mnet1
kubectl exec -it peer0-morg1-7886d746ff-pzbmb --namespace=mnet1 -- /bin/bash
ps aux
ps aus
uname -a
result=$( curl -X GET http://127.0.0.1:5984/_all_dbs )
echo $result | jq 
http://10.114.201.49:32200/_utils/



kubectl cordon <node-name>      # Which will cause the node to be in the status: Ready,SchedulingDisabled.
kubectl uncordon <node-name>    # To tell is to resume scheduling use


验证容器正在运行：
kubectl get pod shell-demo
获取运行容器的 Shell ：
kubectl exec -it peer0-morg1-7886d746ff-pzbmb --namespace=mnet1 -- /bin/bash
在 shell 中列出正在运行的进程：
root@shell-demo:/# ps aux

创建RC：
kubectl create -f *.yaml
查看创建好的RC：
kubectl get rc
查看POD的创建情况:
kubectl get pods
查看创建的service:
kubectl get svc
查看node：
kubectl get nodes
查看某个node信息:
kubectl describe node nodename
通过指令完成POD动态缩放:
kubectl scale rc poname  --replicas=3
查看deployment：
kubectl get deployments
查看对应的replica set :
kubectl get rs
创建HPA对象:
kubectl autoscale deployment pod --cpu-lercent=80 --min=1 --max=1-

术语(node,Pod,Replication,Controller,Service：
1.	master: 指的是集群控制节点，每个kubernetes集群都有一个master节点负责集群的管理和控制所有命令都是发给它执行，通常是一个独立的服务器。运行着kubernetes api，kubernetes controller manager，kubernetes scheduler
2.	Node:除了master节点其他都叫做node节点，每个node运行着kubelet,kube-proxy,docker engine。
3.	Pod:每个pod都有一个pause容器，POD里的容器可以互相通信，
4.	label:键值对,可以用在node,pod,service,rc上,通过lebel来区分对象，可以理解为标签
5.	RC：包括POD副本数，筛选目标POD，POD模板
6.	HEAPSTER:分析POD实现水平扩容
7.	service:微服务，进行通信，每个service 有个虚拟的ip地址，通信节点

## 4.3 Ansible
## 4.4 Gitlab 
## 4.5 Harbor
## 4.6 Jenkins

service jenkins start
service jenkins restart
service jenkins stop

## 4.7 Git

git init
git commit -m "first commit"
git remote add origin https://github.com/mnuestc/vagrant-ansible-k8s-setup.git
git push -u origin 


先查看远程地址：git remote show origin
再修改远程地址：git remote set-url origin <new url>

git branch
git log oneline


## 5 区块链技术
