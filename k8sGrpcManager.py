# -*- coding: utf-8 -*-s
from kubernetes import watch
import time
import grpc
from concurrent import futures
import serviceManager_pb2, serviceManager_pb2_grpc
import json
import requests
import io
import os
from os import path
import yaml
from string import Template
from threading import Thread
from requests.exceptions import ReadTimeout
from analyzer.applications.faultAnalysis import *
import re
import uuid
from analyzer.services.data.paraser import config as IPconfig
import pdb
# import manager.to_deploy_k8s as deploy_k8s
# from manager.to_deploy_k8s import K8sNetworkOperation
from to_deploy_k8s import K8sNetworkOperation
import _thread
import threading
import select
import errno
import datetime as dtime
import sys
# import struct                               # 将字符串打包为二进制流进行网络传输
# import select     
# import signal                               # 用于捕获中断信号
# import pickle                               # 将python对象进行序列化:dumps将python对象序列化保存为字符串,loads与之相反
# from socket import *
from kubernetes import client, config
import socket


hostname = socket.gethostname()
_HOST = socket.gethostbyname(hostname)
print(_HOST,hostname)
_PORT = '55666'


unit_yaml_name = "unit.yaml"
baseDir = os.path.dirname(__file__)
template_dir = os.path.join(baseDir,"template/")
depoloy_dir = os.path.join(baseDir,"depoloy/")
knowledge_graph_unit_template_path = os.path.join(template_dir, unit_yaml_name)

TOPO_INFO = None
containerList = []

print(dtime.datetime.now().strftime("%Y.%m.%d-%H:%M:%S"), time.time())
print(baseDir)
print(depoloy_dir)
print(template_dir)
print(knowledge_graph_unit_template_path)


#解决乱码问题
# print(sys.stdout.encoding)
def setup_io():
    sys.stdout = sys.__stdout__ = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = sys.__stderr__ = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)
setup_io()

#异步调用函数封装
def async_call(func):
    def wrapper(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

# socketServer方式目前已弃用
# HOSTNAME = gethostname()
# IP = gethostbyname(HOSTNAME)
# SOCKET_PORT = 6000
class SServerThread(threading.Thread):                                 
    def __init__(self,HOST,PORT,name=None,backlog = 5):
        threading.Thread.__init__(self,name=name)
        self.host = HOST
        self.port = PORT
        self.backlog = backlog
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)        # 重用套接字地址
        self.server.bind((self.host,self.port))
        self.server.listen(self.backlog)
        self.inputs = [self.server]       
        self.clients = 0
        self.clientmap = {}
        self.outputs = [] 
        self.cnamemap = {}                                      # Client会话列表

    def signalhandler(self,signum,frame):                       # 中断处理方法
        print("Shutting down socket server ...")
        for output in self.outputs:
            output.close()
        self.server.close()

    def get_client_name(self,client):
        info = self.clientmap[client]
        host,port,name = info[0][0],info[0][1],info[1]
        return ':'.join((('@'.join((name,host))),str(port)))

    def send(self,channel,*args):                                # 发送数据
        buffer = pickle.dumps(args)
        value = htonl(len(buffer))
        size = struct.pack("L",value)
        channel.send(size)
        channel.send(buffer)

    def receive(self,channel):                                   # 接收数据
        size = struct.calcsize("L")
        size = channel.recv(size)
        try:
            size = ntohl(struct.unpack("L",size)[0])             # socket.ntohl(参考：http://blog.csdn.net/tatun/article/details/7194973)
        except struct.error as e:
            print(e)
            return ''
        buf = b''
        while len(buf) < size:
            buf += channel.recv(size-len(buf))
        return pickle.loads(buf)[0]                              # 恢复python对象

    @async_call
    def heart_beat(self):
        while True:
            time.sleep(5)
            # msg = MsgFormat.HeartBeat
            msg = {
                'ping': str(uuid.uuid1()),
                'timeStamp': int(round(time.time()*1000))       
            }
            for output in self.outputs:
                self.send(output,msg)         
        pass

    def run(self):

        print('Waiting for connected...')

        self.heart_beat()

        while True:            
            # time.sleep(3)
            # print('servering...')
            try:
                readable,writeable,execption = select.select(self.inputs,self.outputs,[])
            except select.error as e:
                print(e)
                break
            for sock in readable:
                if sock == self.server:                                                     #服务器端接收
                    client,address = self.server.accept()
                    print("Socket server: connected from", address)
                    self.clients += 1
                    cname = self.receive(client)
                    self.send(client,str(address[0]))
                    self.inputs.append(client)
                    self.outputs.append(client) 
                    self.clientmap[client] = (address,cname)
                    self.cnamemap[cname] = client
                    msg = "(Connected : New Client(%d) from %s)\n"%(self.clients,self.get_client_name(client))

                    # self.outputs.append(client) 
                    # print(self.TOPO_INFO)

                    # self.send(client,self.TOPO_INFO) 
                    # socketMessege
                    # print(MsgFormat.resultReq)
                    MsgFormat.ResultReq['messageData'] = {  
                        "TopoID":"globaltopo",
                        "DevID":cname,
                        "BitMap":['0xFFFF']
                    } 
                    self.send(client, MsgFormat.ResultReq) 
                    
                    # 将开始回话的client加入Client回话列表
                    # for output in self.outputs:
                    #     self.send(output,msg)
                #elif sock == sys.stdin:
                    #break

                # if sock == 0:
                #     data = sys.stdin.readline().strip()
                #     if data:
                #         for output in self.outputs:
                #             self.send(output,data)

                else:
                    try:
                        data = self.receive(sock)
                        if data:
                            # dict1 =pickle.load(data)
                            # # data =  json.loads(data)
                            # data = eval(data)
                            # # data = eval(data)
                            # print(dict1)
                            print(type(data))
                            print(data)

                            # msg = '[' + self.get_client_name(sock)+ '] >> ' + data
                            # print(msg)

                            # for output in self.outputs:
                            #     if output!=sock:
                            #         self.send(output,msg)
                        else:
                            self.clients-=1
                            sock.close()
                            self.inputs.remove(sock)
                            self.outputs.remove(sock)
                            # msg = '(Now hung up: Client from %s)'%self.get_client_name(sock)
                            # message = "At present, only one of you is in the chat room!"
                            # for output in self.outputs:
                            #     self.send(output,msg)
                            # if self.clients == 1:
                            #     self.send(self.outputs[0],message)
                    except error as e:
                        print(e)
                        try:
                            self.inputs.remove(sock)
                            self.outputs.remove(sock)
                            pass
                        except error as identifier:
                            print(identifier)
                            pass
        self.server.close()
# SSThread = SServerThread(IP, SOCKET_PORT, name='ssthread')
# SSThread.start()

# yaml替换字段函数
def render(src, dest, **kw):
    t = Template(open(src, 'r').read())
    with open(dest, 'w') as f:
        f.write(t.substitute(**kw))

def getTemplate(templateName):
    baseDir = os.path.dirname(__file__)
    print(baseDir)
    configTemplate = os.path.join(baseDir, "template/" + templateName)
    print(configTemplate)
    return configTemplate

# K8s调度
class K8sScheduler():
    def get_topo(): 
        global containerList 
        # response = make_response()
        # response.headers.set('Content-Type', 'application/json')          
        contex = []        
        ret, topo_url = IPconfig.get_topo_url(contex)        
        headers = {'Content-Type': 'application/json', 'username': 'admin', 'authen': 'DataCore'}        
        # topo_url = 'http://10.96.237.101:8080/NDPBusiness/netTopo/getTopoInfo'
        topo_url = str(topo_url) + "?topoId=globalTopo"  
        print(topo_url)

        try:
            response = requests.get(url=topo_url, headers = headers, timeout=1000).json()
            
        except:
            return  ["exception"]
        else:
            if not os.path.exists(depoloy_dir):
                os.mkdir(depoloy_dir)                
            nodeList = [asset['assetId'] for asset in response['result']['nodes']]
            return nodeList

    # @async_call
    def update_unit(containerList, nodeList, imageName):
        for assetId in nodeList:
            if assetId not in containerList:

                deploymentName = "itoams"+ assetId[:6]
                serviceName = deploymentName
                nameSpace = "itoa"
                # config.load_kube_config()
                config.load_incluster_config()
                K8sScheduler.create_service(serviceName, nameSpace) 


                knowledge_graph_unit_path = os.path.join(depoloy_dir, assetId[:6]+"-"+unit_yaml_name)
                render(knowledge_graph_unit_template_path, knowledge_graph_unit_path,
                assetId=assetId[:6],
                imageName=imageName,
                MANAGER_HOST=_HOST
                )

                operation = K8sNetworkOperation()
                with open(knowledge_graph_unit_path) as f:
                    resources = yaml.load_all(f,Loader=yaml.FullLoader)
                    operation.deploy_k8s_resource(resources)
                    print(resources)
                    print(assetId[:6])     
                containerList.append(assetId)

        for assetId in containerList:
            if assetId not in nodeList:   

                deploymentName = "itoams"+ assetId[:6]
                serviceName = deploymentName
                nameSpace = "itoa"
                # config.load_kube_config()
                config.load_incluster_config()
                K8sScheduler.delete_service(serviceName, nameSpace) 

                time.sleep(2)
                knowledge_graph_unit_path = os.path.join(depoloy_dir, assetId[:6]+"-"+unit_yaml_name)
                render(knowledge_graph_unit_template_path, knowledge_graph_unit_path,
                assetId=assetId[:6],
                MANAGER_HOST=IP
                )
                operation = K8sNetworkOperation()
                with open(knowledge_graph_unit_path) as f:
                    resources = yaml.load_all(f,Loader=yaml.FullLoader)     
                    operation.delete_k8s_resource(resources)
                    print(resources)
                    print(assetId[:6]) 
                containerList.remove(assetId)
                print(containerList)
                time.sleep(2)
        return  containerList        


    def delete_unit(containerList,imageName): 

        while len(containerList) != 0:
            for assetId in containerList:

                deploymentName = "itoams"+ assetId[:6]
                serviceName = deploymentName
                nameSpace = "itoa"

                # K8sScheduler.delete_deployment(api_instance, deploymentName, nameSpace)
                # config.load_kube_config() 
                config.load_incluster_config()
                K8sScheduler.delete_service(serviceName, nameSpace)
                time.sleep(2)

                knowledge_graph_unit_path = os.path.join(depoloy_dir, assetId[:6]+"-"+unit_yaml_name)
                # render(knowledge_graph_unit_template_path, knowledge_graph_unit_path,
                # assetId=assetId[:6],
                # imageName=imageName,
                # MANAGER_HOST=IP
                # )
                # config.load_kube_config()
                # apps_v1 = client.ExtensionsV1beta1Api()
                # extendv1client()
                #AppsV1Api()
                # api_instance = apps_v1

                with open(knowledge_graph_unit_path) as f:

                    resources = yaml.load_all(f,Loader=yaml.FullLoader) 
                    operation = K8sNetworkOperation()  
                    operation.delete_k8s_resource(resources)
                    print(resources,-1)
                    print(assetId[:6])
                time.sleep(2)
                containerList.remove(assetId)
            
        print(containerList)
        return  containerList


    def create_deployment_object(deploymentName, containerName, imageName, containerLable, container_Port):
        # Configureate Pod template container
        container = client.V1Container(
            name=containerName,
            image=imageName
            # ports=[client.V1ContainerPort(containerPort=80)]
            )
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": containerLable}),
            spec=client.V1PodSpec(containers=[container]))
        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=1,
            template=template,
            selector={'matchLabels': {'app': containerLable}})
        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deploymentName),
            spec=spec)

        return deployment


    def create_deployment(api_instance, deployment, nameSpace):
        # Create deployement
        api_response = api_instance.create_namespaced_deployment(
            body=deployment,
            namespace=nameSpace)
        print("Deployment created. status='%s'" % str(api_response.status))


    def update_deployment(api_instance, deployment, deploymentName, nameSpace, imageName):
        # Update container image
        deployment.spec.template.spec.containers[0].image = imageName
        # Update the deployment
        api_response = api_instance.patch_namespaced_deployment(
            name=deploymentName,
            namespace=nameSpace,
            body=deployment)
        print("Deployment updated. status='%s'" % str(api_response.status))


    def delete_deployment(api_instance, deploymentName, nameSpace):
        # Delete deployment
        api_response = api_instance.delete_namespaced_deployment(
            name=deploymentName,
            namespace=nameSpace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print("Deployment deleted. status='%s'" % str(api_response.status))


    def create_service(serviceName, nameSpace):
        core_v1_api = client.CoreV1Api()
        body = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=serviceName
            ),
            spec=client.V1ServiceSpec(
                selector={"app": "deployment"},
                ports=[client.V1ServicePort(
                    port=5050,
                    target_port=5050
                )]
            )
        )
        # Creation of the Deployment in specified namespace
        # (Can replace "default" with a namespace you may have created)
        core_v1_api.create_namespaced_service(namespace=nameSpace, body=body)

    def delete_service(serviceName, nameSpace):
        core_v1_api = client.CoreV1Api()
        core_v1_api.delete_namespaced_service(name=serviceName ,namespace=nameSpace)

    def create_ingress(networking_v1_beta1_api):
        body = client.NetworkingV1beta1Ingress(
            api_version="networking.k8s.io/v1beta1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name="ingress-example", annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/"
            }),
            spec=client.NetworkingV1beta1IngressSpec(
                rules=[client.NetworkingV1beta1IngressRule(
                    host="example.com",
                    http=client.NetworkingV1beta1HTTPIngressRuleValue(
                        paths=[client.NetworkingV1beta1HTTPIngressPath(
                            path="/",
                            backend=client.NetworkingV1beta1IngressBackend(
                                service_port=5678,
                                service_name="service-example")

                        )]
                    )
                )
                ]
            )
        )
        # Creation of the Deployment in specified namespace
        # (Can replace "default" with a namespace you may have created)
        networking_v1_beta1_api.create_namespaced_ingress(
            namespace="default",
            body=body
        )

# K8s测试
class K8sTest():
    def dynamicYamlTest():    
        nodeList = K8sScheduler.get_topo()
        nodeList =  nodeList[:5]
        print(nodeList)
        print("starting updating")

        config.load_kube_config()
        apps_v1 = client.AppsV1Api()
        api_instance = apps_v1

        nameSpace = "itoa"
        imageName = "itoa/itoa-ai:V100R001B02D005SP04"
        container_Port=5050
        for assetId in nodeList:
            deploymentName = "itoams"+ assetId[:6]
            print(deploymentName)
            containerName = deploymentName
            containerLable = deploymentName
            serviceName = deploymentName
            print(containerName)
            deployment = K8sScheduler.create_deployment_object(deploymentName, containerName, imageName, containerLable, container_Port)
            K8sScheduler.create_deployment(api_instance, deployment, nameSpace)
            K8sScheduler.create_service(serviceName, nameSpace)

        time.sleep(10)

        print("starting deleting")
        for assetId in nodeList:
            deploymentName = "itoams"+ assetId[:6]
            serviceName = deploymentName
            K8sScheduler.delete_deployment(api_instance, deploymentName, nameSpace)
            K8sScheduler.delete_service(serviceName, nameSpace)

    def staticYamlTest():    
        nodeList = K8sScheduler.get_topo()
        nodeList =  nodeList[:5]
        print(nodeList)
        print("starting updating")

        config.load_kube_config()

        nameSpace = "itoa"
        imageName = "itoa/itoa-ai:V100R001B02D005SP04"
        container_Port=5050

        K8sScheduler.update_unit([], nodeList, imageName)

        time.sleep(10)
        print("starting deleting")
        K8sScheduler.delete_unit(nodeList, imageName) 


# grpc服务
class ManagerServicer(serviceManager_pb2_grpc.ServiceManagerServicer):

    def CreateService(self, request, context):

        result = "CRE:" + request.ServiceName + "尚不需要实现"
        return serviceManager_pb2.CreateReply(CreateResult=result.upper())

    def DeleteService(self, request, context):
        result = "DEL:" + request.ServiceName 
        c = containerList
        print(len(c),c)
        imageName = request.ServiceName
        r = K8sScheduler.delete_unit(c,imageName)
        return serviceManager_pb2.UpdateReply(UpdateResult=result.upper()+str(r))

    def UpdateService(self, request, context):
        n = K8sScheduler.get_topo()
        c = containerList

        imageName = request.ServiceName

        r = K8sScheduler.update_unit(c,n,imageName)
        result = "UPD:" + request.ServiceName
        return serviceManager_pb2.UpdateReply(UpdateResult=result.upper()+str(r))

    def CheckService(self, request, context):
        result = "CHE:" + request.ServiceName
        return serviceManager_pb2.CheckReply(CheckResult=result.upper())

def main():
      
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))                            # 创建一个服务器,定义服务器并设置最大连接数, corcurrent.futures是一个并发库，类似于线程池的概念
    serviceManager_pb2_grpc.add_ServiceManagerServicer_to_server(ManagerServicer(), grpcServer)     # 在服务器中添加派生的接口服务（自己实现了处理函数）
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)                                               # 添加监听端口
    grpcServer.start()                                                                              # 启动服务器    
    
    try:
        while True:
            print("running...")
            time.sleep(1000)
            # time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print("stopping...")
        grpcServer.stop(0) # 关闭服务器

def initing():
    config.incluster_config()  
    # config.load_kube_config()
    core_v1_api = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    deployNameList=[]
    serviceNameList=[]
    allNameList=[]
    w = watch.Watch()
    #count =10
    for event in w.stream(apps_v1.list_deployment_for_all_namespaces, timeout_seconds=10):
        # print("Event: %s %s %s" % (
        #     event['type'],
        #     event['object'].kind,
        #     event['object'].metadata.name)           
        # )
        allNameList.append(event['object'].metadata.name)
        if event['object'].metadata.name[0:6] == "itoams":           
            deployNameList.append(event['object'].metadata.name)
        # count -= 1
        # if not count:
        #     w.stop()
    for event in w.stream(core_v1_api.list_service_for_all_namespaces, timeout_seconds=10):       
        # serviceNameList.append(event['object'].metadata.name[0:6] )
        if event['object'].metadata.name[0:6] == "itoams":
            serviceNameList.append(event['object'].metadata.name)
    print(allNameList)
    print(deployNameList)
    print(serviceNameList)

    try:
        # while len(deployNameList) != 0:
        for deploymentName in deployNameList:
            nameSpace = "itoa"
            
            K8sScheduler.delete_deployment(apps_v1, deploymentName, nameSpace)

        # while len(serviceNameList) != 0:
        for serviceName in serviceNameList:
            nameSpace = "itoa"
            K8sScheduler.delete_service(serviceName, nameSpace)    
            pass
    except Expression as identifier:
        print(identifier)
        pass

          

if __name__ == '__main__':
    initing()




    main()                   
    # 测试函数
    # K8sTest.dynamicTest()
    # K8sTest.staticYamlTest()
    
