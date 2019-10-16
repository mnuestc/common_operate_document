# 第1章 k8s外部不能访问pod
1、问题描述：
在搭建好的k8s集群内创建的容器，只能在其所在的节点上curl可访问，但是在其他任何主机上无法访问容器占用的端口
1.1、解决方案
vim /etc/sysctl.conf
找到这一行，放开注释
#Uncomment the next line to enable packet forwarding for IPv4
net.ipv4.ip_forward=1
重启主机（必须要重启才能生效）

# 第2章 创建私有仓库问题
2.1、问题描述，提示需要https协议问题解决
[root@docker docker]# docker push 10.0.0.10:5000/test/nginx:v1
The push refers to repository [10.0.0.10:5000/test/nginx]
Get https://10.0.0.10:5000/v2/: http: server gave HTTP response to HTTPS client
2.1.1、解决方法1：（docker 1.2以上版本解决方法）
在/etc/docker/daemon.json添加以下信息
{ "insecure-registries":["10.0.0.10:5000"]   必须要加在第一行
重启docker，重启registry
systemctl restart docker.service
2.1.2、解决方法2：（docker1.2以下版本解决方法）

报错信息2：
[root@lnmp ~]# docker pull 10.0.0.10:5000/test/nginx:v1
Error response from daemon: invalid registry endpoint https://10.0.0.10:5000/v0/: unable to ping registry endpoint https://10.0.0.10:5000/v0/
v2 ping attempt failed with error: Get https://10.0.0.10:5000/v2/: tls: oversized record received with length 20527
v1 ping attempt failed with error: Get https://10.0.0.10:5000/v1/_ping: tls: oversized record received with length 20527. If this private registry supports only HTTP or HTTPS with an unknown CA certificate, please add `--insecure-registry 10.0.0.10:5000` to the daemon's arguments. In the case of HTTPS, if you have access to the registry's CA certificate, no need for the flag; simply place the CA certificate at /etc/docker/certs.d/10.0.0.10:5000/ca.crt

2.2、解决办法：

在/etc/sysconfig/docker中添加如下信息即可
other_args="--insecure-registry 10.0.0.10:5000"     私有仓库地址
other_args="--insecure-registry registry:5000"      公有仓库地址
重启docker，重启registry
/etc/init.d/docker restart

# 第3章 下载镜像出现问题
3.1、问题1：提示/etc/rhsm/ca/redhat-uep.pem no file or dirctory
3.1.1、解决方法：
3.1.1.1、yum安装需要的依赖包

yum -y install *rhsm*
1
3.1.1.2、下载python-rhsm-certificates软件并生成密钥文件

wget http://mirror.centos.org/centos/7/os/x86_64/Packages/python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm
生成密钥
rpm2cpio python-rhsm-certificates-1.19.10-1.el7_4.x86_64.rpm | cpio -iv --to-stdout ./etc/rhsm/ca/redhat-uep.pem | tee /etc/rhsm/ca/redhat-uep.pem
1
2
3
3.1.1.3、重新pull镜像

docker pull registry.access.redhat.com/rhel7/pod-infrastructure:latest
1
第4章 不能删除容器
4.1、docker报错rpc error: code = 14 desc = grpc: the connection is unavailable
4.1.1、尝试关闭容器，进入容器操作界面也报相同错误：

[root@k8s-node-1 ~]# docker exec -it 7119f8f5feef /bin/bash
rpc error: code = 14 desc = grpc: the connection is unavailable
1
2
4.1.1.2、停止容器依旧提示错误

[root@k8s-node-1 ~]# docker stop 7119f8f5feef
Error response from daemon: Cannot stop container 7119f8f5feef: Cannot kill container 7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327: rpc error: code = 14 desc = grpc: the connection is unavailable
1
2
4.1.1.3、删除容器依旧提示错误（-f强制删除）

[root@k8s-node-1 ~]# docker rm -f 7119f8f5feef
Error response from daemon: Could not kill running container 7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327, cannot remove - Cannot kill container 7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327: rpc error: code = 14 desc = grpc: the connection is unavailable
1
2
4.2、解决办法：
4.2.1、使用docker-containerd命令以debug模式调试容器
注意：那个node上的容器不能删除就在那台node上面执行以下命令

[root@k8s-node-1 ~]# docker-containerd -l unix:///var/run/docker/libcontainerd/docker-containerd.sock --metrics-interval=0 --start-timeout 2m --state-dir /var/run/docker/libcontainerd/containerd --shim docker-containerd-shim --runtime docker-runc --debug
WARN[0000] containerd: low RLIMIT_NOFILE changing to max  current=1024 max=4096
DEBU[0000] containerd: read past events                  count=1
 low RLIMIT_NOFILE changing to max  current=1024 max=4096DEBU[0000] containerd: grpc api on /var/run/docker/libcontainerd/docker-containerd.sock 
DEBU[0000] containerd: container restored                id=354af53914e3f76e653a26d9e9da8d4fbef4ef18cc2176371b89871a9126a646
DEBU[0000] containerd: container restored                id=3f0bf43f7ca97c439b64370cee09205b35e58ed35e49f957412f58affbe4ed4b
DEBU[0000] containerd: container restored                id=4b848d33a32a332635929b95eb7291abeb32f177a3c65248568b959dbfbc2712
DEBU[0000] containerd: container restored                id=4ed8d1f971a0ea5035b507511d802a1445af9e771cde670814104102a7cc2d6f
ERRO[0000] containerd: notify OOM events                 error=open /proc/13541/cgroup: no such file or directory
DEBU[0000] containerd: container restored                id=7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327
ERRO[0000] containerd: notify OOM events                 error=open /proc/12860/cgroup: no such file or directory
DEBU[0000] containerd: container restored                id=7bdba0a1ee81997bdbb5958e31123538ac8a6730c6cc7120fe7359439b52b410
DEBU[0000] containerd: container restored                id=8ba79a79836b4350335375f89fc1473a6a86593375fbac6344fb17e4dddff43f
DEBU[0000] containerd: container restored                id=9692f3570460186de681476bd068d008891b24b3906f190443f24e97343c3e57
DEBU[0000] containerd: supervisor running                cpus=1 memory=977 runtime=docker-runc runtimeArgs=[] stateDir=/var/run/docker/libcontainerd/containerd
DEBU[0000] containerd: process exited                    id=7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327 pid=init status=143 systemPid=13541
ERRO[0000] containerd: deleting container                error=exit status 1: "container 7119f8f5feef4c649d9ec04734e6224e2d837fa030de271f269f0b71eea29327 does not exist\none or more of the container deletions failed\n"
DEBU[0000] containerd: process exited                    id=7bdba0a1ee81997bdbb5958e31123538ac8a6730c6cc7120fe7359439b52b410 pid=init status=137 systemPid=12860
ERRO[0000] containerd: deleting container                error=exit status 1: "container 7bdba0a1ee81997bdbb5958e31123538ac8a6730c6cc7120fe7359439b52b410 does not exist\none or more of the container deletions failed\n"

^CINFO[0056] stopping containerd after receiving interrupt
4.2.2、调试后发现容器状态变为了未开启，尝试删除容器，成功

docker exec -it 3e22bd0b6a40 /bin/bash
Error response from daemon: Container 3e22bd0b6a40c85d2af45b5d65fb3648acab7e0ad05fa909201051a8f00a3d15 is not running
docker rm -f zen_mclean 
zen_mclean
1
2
3
4
# 第5章 k8s下DNS问题
5.1、kubelet提示DNS错误信息

kubelet does not have ClusterDNS IP configured and cannot create Pod using "ClusterFirst" policy. Fail
1
5.2、解决办法：

在cat /etc/kubernetes/kubelet 配置文件中添加如下内容即可
KUBE_ARGS="--cluster-dns=10.0.0.110 --cluster-domain=cluster.local"
重启 systemctl daemon-reload;  systemctl restart kubelet 即可
1
2
3
第6章 docker run （镜像）报错，文件系统不支持
1、报错信息如下：

/usr/bin/docker-current: Error response from daemon: error creating overlay mount to /var/lib/docker/overlay2/7b4a1ef8a539785fde3fa4cabc4bb9d90967a30calid argument.
See '/usr/bin/docker-current run --help'.
1
2
2、报错原因

这个是因为用的overlay2文件系统，而系统默认只能识别overlay文件系统
所以我们就要更新文件系统了
1
2
3、解决方法：

systemctl stop docker              //停掉docker服务
rm -rf /var/lib/docker             //注意会清掉docker images的镜像
vi /etc/sysconfig/docker-storage   //将文件里的overlay2改成overlay即可
DOCKER_STORAGE_OPTIONS="--storage-driver overlay2 "  #修改前
DOCKER_STORAGE_OPTIONS="--storage-driver overlay "   #修改后
vi /etc/sysconfig/docker           //去掉option后面的--selinux-enabled
1
2
3
4
5
6
4、重新启动docker即可

systemctl start docker
1
第7章 docker运行apache报错
7.1、报错信息如下：

[root@k8s-node-3 ~]# docker logs 99e3fc059214
WordPress not found in /var/www/html - copying now...
Complete! WordPress has been successfully copied to /var/www/html
AH00534: apache2: Configuration error: No MPM loaded.
1
2
3
4
7.2、解决方法：

systemctl stop docker              //停掉docker服务
rm -rf /var/lib/docker             //注意会清掉docker images的镜像
vi /etc/sysconfig/docker-storage   //将文件里的overlay2改成devicemapper即可
DOCKER_STORAGE_OPTIONS="--storage-driver overlay2 "  #修改前
DOCKER_STORAGE_OPTIONS="--storage-driver devicemapper "   #修改后
1
2
3
4
5
7.3、重启docker服务

systemctl start docker
1
第8章 启动pod报错信息如下：

[root@k8s_master k8s_yaml]# kubectl -n ingress-nginx get events  #通过事件查看错误信息

Warning   FailedCreate        ReplicaSet   Error creating: pods "nginx-ingress-controller-9fc7f4c5f-5f2k4" is forbidden: SecurityContext.RunAsUser is forbidden
7m42s       Warning   FailedCreate        ReplicaSet   Error creating: pods "nginx-ingress-controller-9fc7f4c5f-25wr7" is forbidden: SecurityContext.RunAsUser is forbidden
1
2
3
4
8.1、解决办法：

修改apiserver配置文件，将SecurityContextDeny去掉，重启kube-apiserver即可解决
————————————————
版权声明：本文为CSDN博主「ljx1528」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/ljx1528/article/details/81437106















# 1. Pod始终处于Pending状态
如果Pod保持在Pending的状态，意味着无法被正常的调度到节点上。由于某种系统资源无法满足Pod运行的需求
系统没有足够的资源：已经用尽了集群中所有的CPU或内存资源。
用户指定了hostPort：通过hostPort用户能够将服务暴露到指定的主机端口上，会限制Pod能够被调度运行的节点。
 

# 2. Pod始终处于Waiting状态
Pod处在Waiting的状态，说明已经被调度到了一个工作节点，却无法在那个节点上运行。
可以使用kubectl describe 含有更详细的错误信息。最经常导致Pod始终Waiting的原因是无法下载镜像

 

# 3. Pod 处于 CrashLoopBackOff 状态
CrashLoopBackOff 状态说明容器曾经启动了，但又异常退出了。此时 Pod 的 RestartCounts 通常是大于 0
容器进程退出
健康检查失败退出
OOMKilled
 

# 5. Pod一直崩溃或运行不正常
可以使用kubectl describe以及kubectl logs排查问题，但是这个一般也不确定
情况有：健康检测失败，OOM情况，或者容器运行生命周期结束

 

# 6. 集群雪崩需给Kubelet预留资源
https://my.oschina.net/jxcdwangtao/blog/1629059

Node Allocatable Resource = Node Capacity - Kube-reserved - system-reserved - eviction-threshold
--eviction-hard=memory.available<1024Mi,nodefs.available<10%,nodefs.inodesFree<5% \
--system-reserved=cpu=0.5,memory=1G \ --kube-reserved=cpu=0.5,memory=1G \
--kube-reserved-cgroup=/system.slice/kubelet.service \
--system-reserved-cgroup=/system.slice \
--enforce-node-allocatable=pods,kube-reserved,system-reserved \


# 7. nfs挂载错误wrong fs type, bad option, bad superblock
根据错误提示，查看/sbin/mount.<type>文件，果然发现没有/sbin/mount.nfs的文件，安装nfs-utils即可

 

 

# 8. kube-apiserver accept4: too many open files

http: Accept error: accept tcp 0.0.0.0:6443: accept4: too many open files; retrying in 1s

    查看apiserver进程，lsof -p $pid，发现占用65540个，查看cat /proc/$pid/limits发现限制在65536个，查看占用的一大堆10250的某个kubelet，发现如下错误

     perationExecutor.UnmountVolume started for volume "makepool1-web3" (UniqueName: "kubernetes.io/nfs/7be05590-3a46-11e9-906c-20040fedf0bc-makepool1-web3") pod "7be05590-3a46-11e9-906c-20040fedf0bc" (UID: "7be05590-3a46-11e9-906c-20040fedf0bc")

    nestedpendingoperations.go:263] Operation for "\"kubernetes.io/nfs/7be05590-3a46-11e9-906c-20040fedf0bc-makepool1-web3\" (\"7be05590-3a46-11e9-906c-20040fedf0bc\")" failed. No retries permitted until 2019-03-07 12:31:28.78976568 +0800 CST m=+7328011.532812666 (durationBeforeRetry 2m2s). Error: "UnmountVolume.TearDown failed for volume \"makepool1-web3\" (UniqueName: \"kubernetes.io/nfs/7be05590-3a46-11e9-906c-20040fedf0bc-makepool1-web3\") pod \"7be05590-3a46-11e9-906c-20040fedf0bc\" (UID: \"7be05590-3a46-11e9-906c-20040fedf0bc\") : Unmount failed: exit status 16\nUnmounting arguments: /var/lib/kubelet/pods/7be05590-3a46-11e9-906c-20040fedf0bc/volumes/kubernetes.io~nfs/makepool1-web3\nOutput: umount.nfs: /var/lib/kubelet/pods/7be05590-3a46-11e9-906c-20040fedf0bc/volumes/kubernetes.io~nfs/makepool1-web3: device is busy\n\n"

    目前解决方案：
    kubectl delete --grace-period=0 --force
    https://github.com/kubernetes/kubernetes/issues/51835

     

# 9. Kubernetes Pod无法删除,Docker: Device is busy问题的解决
   参考： https://fav.snadn.cn/article/snapshot?id=131#问题发现

 

 

# 10. k8s 证书过期，一年时间，
2. 自动轮换 kubelet 证书
注：kubelet证书分为server和client两种， k8s 1.9默认启用了client证书的自动轮换，但server证书自动轮换需要用户开启。方法是：

2.1 增加 kubelet 参数
--feature-gates=RotateKubeletServerCertificate=true

2.2 增加 controller-manager 参数
--experimental-cluster-signing-duration=87600h0m0s
--feature-gates=RotateKubeletServerCertificate=true

2.3 创建 rbac 对象
创建rbac对象，允许节点轮换kubelet server证书：

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
rules:
- apiGroups:
  - certificates.k8s.io
  resources:
  - certificatesigningrequests/selfnodeserver
  verbs:
  - create
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kubeadm:node-autoapprove-certificate-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:nodes
 

# 11. k8s无法删除namespace 提示 Terminating
解决方法：

kubectl get ns ns-xxx-zhangzhonglin-444c6833 -o json > ns-delete.json

删除文件中spec.finalizers字段

"spec": {
    },

   注：在执行命令前，要先克隆一个新会话，执行 kubectl proxy --port=8081

curl -k -H "Content-Type: application/json" -X PUT --data-binary @ns-delete.json http://127.0.0.1:8081/api/v1/namespaces/ns-xxx-zhangzhonglin-444c6833/finalize

 

# 12. Kubernetes: No Route to Host
     Error getting server version: Get https://10.200.0.1:443/version?timeout=32s: dial tcp 10.200.0.1:443: connect: no route to host

     解决方法： iptables -F


# 13. kubeadm kube-controller-manager does not have ceph rbd binary anymore   
Error: "failed to create rbd image: executable file not found in $PATH, command output: "
   https://github.com/kubernetes/kubernetes/issues/56990
   yum install -y ceph-common

 

# 14. monclient: _check_auth_rotating possible clock skew, rotating keys expired way too early (before 2019-05-06 02:00:09.601676)
     ceph osd问题，主要是时钟不同步问题

 

# 15. helm报这个错误 Helm: Error: no available release name found
        因为 tiller没有正确的角色权限

kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'

 

# 16.  attachdetach-controller  Multi-Attach error for volume "pvc-d0fde86c-8661-11e9-b873-0800271c9f15" Volume is already used by pod
    The controller-managed attachment and detachment is not able to detach a rbd volume from a lost node #62061

    https://github.com/kubernetes/kubernetes/issues/70349

    https://github.com/kubernetes/kubernetes/pull/45346

    https://github.com/kubernetes/kubernetes/issues/53059

    https://github.com/kubernetes/kubernetes/pull/40148

   Vsphere Cloud Provider: failed to detach volume from shutdown node #75342       

   Don't try to attach volumes which are already attached to other nodes #45346

   Pods with volumes stuck in ContainerCreating after cluster node is deleted from OpenStack #50200

   Don't try to attach volumes which are already attached to other nodes#40148

   Pods with volumes stuck in ContainerCreating after cluster node is powered off in vCenter #50944

   Pod mount Ceph RDB volumn failed due to timeout. "timeout expired waiting for volumes to attach or mount for pod" #75492 (没人跟帖)

 

# 17. kubelet 挂掉，csi-rbdplugin 依然建在（statefuleset）

 

# 18. k8s pv无法删除问题
  pv始终处于“Terminating”状态，而且delete不掉

 删除k8s中的记录   kubectl patch pv xxx -p '{"metadata":{"finalizers":null}}'

 

 

# 19. Volumes fail to clean up when kubelet restart due to race between actual and desired state #75345    
   Fix race condition between actual and desired state in kublet volume manager #75458

  Pod is stuck in Terminating status forever after Kubelet restart #72604

 

# 20. when using ValidatingWebhookConfiguration for deployment subresource(scale) validation. Internal error occurred: converting (extensions.Deployment).Replicas to (v1beta1.Scale).Replicas: Selector not present in src
   该问题已经修复，v15版本

   https://github.com/kubernetes/kubernetes/pull/76849/commits

 
# 21. Error from server: Get https://master-node:10250/containerLogs/default/csi-hostpathplugin-0/node-driver-registrar: dial tcp: lookup master-node on 114.114.114.114:53: no such host
     解决方法，在 /etc/hosts 添加 192.168.X.X master-node

 

# 22. 无法删除image报rbd: error: image still has watchers解决方法
     参考. 无法删除image报rbd: error: image still has watchers解决方法

解决思路：
在Ceph集群日常运维中，管理员可能会遇到有的image删除不了的情况：
1） 由于image下有快照信息，只需要先将快照信息清除，然后再删除该image即可
2） 该image仍旧被一个客户端在访问，具体表现为该image中有watcher。如果该客户端异常了，那么就会出现无法删除该image的情况

对于第一种情况，很好解决，下面要说的是第二种情况该如何解决。解决之前先科普一下watcher相关的知识：
Ceph中有一个watch/notify机制(粒度是object)，它用来在不同客户端之间进行消息通知，使得各客户端之间的状态保持一致，而每一个进行watch的客户端，对于Ceph集群来说都是一个watcher。

解决方法：
1. 查看当前image上的watcher
查看方法一：
[root@node3 ~]# rbd status foo
watcher=192.168.197.157:0/1135656048 client.4172 cookie=1
这种查看方法简单快捷，值得推荐

查看方法二：
1） 首先找到image的header对象

[root@node3 ~]# rbd info foo
rbd image 'foo':
        size 1024 MB in 256 objects
        order 22 (4096 kB objects)
        block_name_prefix: rbd_data.1041643c9869
        format: 2
        features: layering
        flags: 
        create_timestamp: Tue Oct 17 10:20:50 2017
由该image的block_name_prefix为 rbd_data.1041643c9869，可知该image的header对象为rbd_header.1041643c9869，得到了header对象后，查看watcher信息

2） 查看该image的header对象上的watcher信息

[root@node3 ~]# rados -p rbd listwatchers rbd_header.1041643c9869
watcher=192.168.197.157:0/1135656048 client.4172 cookie=1
2. 删除image上的watcher
2.1 把该watcher加入黑名单：
[root@node3 ~]# ceph osd blacklist add 192.168.197.157:0/1135656048 
blacklisting 192.168.197.157:0/1135656048 until 2017-10-18 12:04:19.103313 (3600 sec)
2.2 查看占用该image的watcher：
[root@node3 ~]# rados -p rbd listwatchers  rbd_header.1041643c9869
[root@node3 ~]# 
异常客户端的watcher信息已经不存在了，之后我们就可以对该image进行删除操作了

2.3 删除该image：
[root@node3 ~]# rbd rm foo
Removing image: 100% complete...done.
3. 后续操作
实际上做完上面的已经解决了问题，不过最好还是把加入黑名单的客户端移除，下面是有关黑名单的相关操作

3.1 查询黑名单列表：
[root@node3 ~]# ceph osd blacklist ls
listed 1 entries
192.168.197.157:0/1135656048 2017-10-18 12:04:19.103313
3.2 从黑名单移出一个客户端：
[root@node3 ~]# ceph osd blacklist rm 192.168.197.157:0/1135656048 
un-blacklisting 192.168.197.157:0/1135656048
3.3 清空黑名单：
[root@node3 ~]# ceph osd blacklist clear
 removed all blacklist entries
————————————————
版权声明：本文为CSDN博主「张忠琳」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/zhonglinzhang/article/details/85257134