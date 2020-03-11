# -*- coding: utf-8 -*
import json
import requests
import time
import os
from os import path
import yaml
from string import Template
from kubernetes import client, config
from kubernetes.client.rest import ApiException
# import log
# from log import log_handler, LOG_LEVEL
import logging

log_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]"
                              " [%(filename)s:%(lineno)s %(funcName)20s()]"
                              " - %(message)s")
log_handler.setFormatter(formatter)
LOG_LEVEL = eval("logging." + os.environ.get("LOG_LEVEL", "INFO"))

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(log_handler)



# token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJpdG9hIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Iml0b2Eta25vd25sZWRnZS1ncmFwaC10b2tlbi01YnN4dyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJpdG9hLWtub3dubGVkZ2UtZ3JhcGgiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyMjE1MmUzNi1mYmFmLTExZTktODMxYS0wNGQ3YTUzZmJjNGMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6aXRvYTppdG9hLWtub3dubGVkZ2UtZ3JhcGgifQ.OPBw0exOLladu_PIBct1OWX6LKdbeZrk3mrLR5E_O2aWQgFlb81gig6VpAvyMd3m8Xb41h6ay2TGIkOpHGso43vT5w3zD22RSDeFz2SlVqrlWY9ebO7ETTCAwnm0yzqT8u1KMI4Zzng9NBWlc5zrPFm1svSm2P84SKXJnbzAA_Oh8bOAHr7LOxplvHqFwtAU2XjbvRzzR0WTVRHpb8RQiJMGWV7JWoIjDyx1HF-mwJjcrSJEDrWJvb-iQS_FyT7hLGqm6PkB5btd1S3qrI8ckvSEug4FMVCxchmBOD2UHH9p0n6wo0yqUxefhi1rTlTOp-ecV7Azd95MWgQpXM9zXg"
# token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJpdG9hIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Iml0b2EtYXBwLW1nci10b2tlbi10cHBjNyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJpdG9hLWFwcC1tZ3IiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiI4MzIzN2NhZS1mYmMyLTExZTktODMxYS0wNGQ3YTUzZmJjNGMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6aXRvYTppdG9hLWFwcC1tZ3IifQ.VdivC90C3Z0xk_Sjgf-CsLgmkIYhtLX9WnFG-1jpCJflrPcTTqsuOPG_lUNrFtkX0kueAKVGRWXQbo1a5C5lPd_9GKD-ZJlU0ZqEatOe44YU5tQQjyApPHkL2Qz-hdsHGKOVlYP3GR4Za9-9WNXu1cG00OOHlQsJ7FuYiyCFaUCpvWXy7QA9otgL8UtonJjF_eKO1yTduzUuVKSf9Tag8fCQ8HW9auiLvvM9gBDkLhQ_j32txa-qxlrhtKcD3lFmuiC6RmlW-QyX3SpozJdJXtnpexoaft-MCsopNSIfathd6bsWQ1ZDrKlZxsTzlGZi3dZC3Pene-Y1LNjWB0y3kQ"
# k8s_url = "https://10.114.134.246:6443"

class K8sNetworkOperation():
    """
    Object to operate cluster on kubernetes
    """
    def __init__(self):
    #def __init__(self, kube_config):
        config.load_incluster_config()            
        # config.kube_config.load_kube_config(config_file="/etc/kubernetes/admin.conf")

        # client.Configuration.set_default(kube_config)
        # configuration = client.Configuration()
        # configuration.host = k8s_url
        # configuration.verify_ssl = False
        # configuration.api_key = {"authorization": "Bearer " + token}

        self.extendv1client = client.AppsV1Api()
        # ExtensionsV1beta1Api()
        # client.AppsV1Api()
        # client.ExtensionsV1beta1Api()
        self.corev1client = client.CoreV1Api()
        # AppsV1Api()
        self.appv1beta1client = client.AppsV1beta1Api()
        self.support_namespace = [
            'Deployment', 
            'Service',
            'PersistentVolumeClaim', 
            'StatefulSet', 
            'ConfigMap'
        ]
        self.create_func_dict = {
            "Deployment": self._create_deployment,
            "Service": self._create_service,
            "PersistentVolume": self._create_persistent_volume,
            "PersistentVolumeClaim": self._create_persistent_volume_claim,
            "Namespace": self._create_namespace,
            "StatefulSet": self._create_statefulset,
            "ConfigMap": self._create_configmap
        }
        self.delete_func_dict = {
            "Deployment": self._delete_deployment,
            "Service": self._delete_service,
            "PersistentVolume": self._delete_persistent_volume,
            "PersistentVolumeClaim": self._delete_persistent_volume_claim,
            "Namespace": self._delete_namespace,
            "StatefulSet": self._delete_statefulset,
            "ConfigMap": self._delete_configmap
        }

    def get_one_availabe_node_ip(self):
        try:
            nodes = self.corev1client.list_node(watch=False)
            for item in nodes.items:
                for con in item.status.conditions:
                    if con.type == 'Ready' and con.status == 'True':
                        for address in item.status.addresses:
                            if address.type == "InternalIP":
                                return address.address
            return None
        except Exception as e:
            logger.error("Kubernetes get node list error msg: {}".format(e))
            return None

    def list_namespaced_pods(self, namespace, label_selector=None):
        try:
            if label_selector is None:
                pods = self.corev1client.list_namespaced_pod(namespace=namespace, watch=False)
            else:
                pods = self.corev1client.list_namespaced_pod(namespace=namespace, label_selector=label_selector, watch=False)
            return pods
        except Exception as e:
            logger.error("Kubernetes get node list error msg: {}".format(e))
            return None

    def deploy_k8s_resource(self, yaml_data):
        for data in yaml_data:
            if data is None:
                continue
            kind = data.get('kind', None)
            name = data.get('metadata').get('name', None)
            namespace = data.get('metadata').get('namespace', None)
            logs = "Deploy namespace={}, name={}, kind={}".format(namespace,
                                                                name, 
                                                                kind)
            # logger.info(logs)
            print(logs)

            if kind in self.support_namespace:
                self.create_func_dict.get(kind)(namespace, data)
            else:
                self.create_func_dict.get(kind)(data)
            time.sleep(3)

    def delete_k8s_resource(self, yaml_data):
        for data in yaml_data:
            if data is None:
                continue
            kind = data.get('kind', None)
            name = data.get('metadata').get('name', None)
            namespace = data.get('metadata').get('namespace', None)

            body = client.V1DeleteOptions()

            logs = "Delete namespace={}, name={}, kind={}".format(namespace,
                                                                  name,
                                                                  kind)
            # logger.info(logs)
            print(logs)

            if kind in self.support_namespace:
                print("kind in self.support_namespace")
                self.delete_func_dict.get(kind)(name, namespace, body)
            else:
                self.delete_func_dict.get(kind)(name, body)
            time.sleep(3)

    def _create_statefulset(self, namespace, data, **kwargs):
        try:
            resp = self.appv1beta1client.create_namespaced_stateful_set(namespace,
                                                                        data,
                                                                        **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _create_configmap(self, namespace, data, **kwargs):
        try:
            resp = self.corev1client.create_namespaced_config_map(namespace,
                                                                    data,
                                                                    **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)


    def _create_deployment(self, namespace, data, **kwargs):
        try:
            resp = self.extendv1client.create_namespaced_deployment(namespace,
                                                                    data,
                                                                    **kwargs)
            # logger.debug(resp)
            # print(resp)
            print("creating deployment: \n " + str(data))
        except ApiException as e:
            print(e)
            # logger.error(e)
        except Exception as e:
            print(e)
            # logger.error(e)
        
    def _create_service(self, namespace, data, **kwargs):
        try:
            resp = self.corev1client.create_namespaced_service(namespace,
                                                               data,
                                                               **kwargs)
            # logger.debug(resp)
            # print(resp)
            print("creating service: \n " + str(data))
        except ApiException as e:
            print(e)
            # logger.error(e)
        except Exception as e:
            print(e)
            # logger.error(e)

    def _create_persistent_volume_claim(self, namespace, data, **kwargs):
        try:
            resp = self.corev1client.\
                create_namespaced_persistent_volume_claim(namespace,
                                                          data,
                                                          **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _create_persistent_volume(self, data, **kwargs):
        try:
            resp = self.corev1client.create_persistent_volume(data, **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _create_namespace(self, data, **kwargs):
        try:
            resp = self.corev1client.create_namespace(data, **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_statefulset(self, name, namespace, data, **kwargs ):
        try:
            resp = self.appv1beta1client.\
                delete_namespaced_stateful_set(name, namespace,
                                                       data, **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_configmap(self, namespace, data, **kwargs):
        try:
            resp = self.corev1client.delete_namespaced_config_map(namespace,
                                                                  data,
                                                                  **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_persistent_volume_claim(self, name, namespace, data, **kwargs):
        try:
            resp = self.corev1client.\
                delete_namespaced_persistent_volume_claim(name, namespace,
                                                          data, **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_persistent_volume(self, name, data, **kwargs):
        try:
            resp = self.corev1client.delete_persistent_volume(name, data,
                                                              **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_service(self, name, data, namespace, **kwargs):
        try:
            # delete_namespaced_service does not need data actually.
            resp = self.corev1client.delete_namespaced_service(name,
                                                               namespace,
                                                               **kwargs)
            # logger.debug(resp)
            print("deleting service " + name + " \n" + str(data))
        except ApiException as e:
            # logger.error(e)
            print("ApiException:", e)
        except Exception as e:
            # logger.error(e)
            print("Exception:", e)

    def _delete_namespace(self, name, data, **kwargs):
        try:
            resp = self.corev1client.delete_namespace(name, data, **kwargs)
            logger.debug(resp)
        except ApiException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

    def _delete_deployment(self, name, namespace, data, **kwargs):
        try:
            resp = self.extendv1client.\
                delete_namespaced_deployment(name, namespace,
                                              **kwargs)
            # logger.debug(resp)
            # print(resp)
            print("deleting deployment " + name + " \n" + str(data))
        except ApiException as e:
            # logger.error(e)
            print(e)
        except Exception as e:
            print(e)
            # logger.error(e)

def render(src, dest, **kw):
	t = Template(open(src, 'r').read())
	with open(dest, 'w') as f:
		f.write(t.substitute(**kw))

def getTemplate(templateName):
	baseDir = os.path.dirname(__file__)
	configTemplate = os.path.join(baseDir, "template/" + templateName)
	return configTemplate

if __name__ == '__main__': 
    print("using k8s")

    # topo_url = 'http://177.177.175.79:8080/NDPBusiness/netTopo/getTopoInfo'
    # topo_url = topo_url + "?topoId=globalTopo"
    # headers = {'Content-Type': 'application/json', 'username': 'admin', 'authen': 'DataCore'}
    # response = requests.get(url=topo_url, headers=headers, timeout=1000).json()
    # node_set = {id['assetId'] for id in response['result']['nodes']}
    # print(node_set)
    # container_set = {}
    # container_set = set(container_set)
    # node_set = set(node_set)
    # deployAnalyzer(container_set, node_set)

#     #client.ExtensionsV1beta1Api().delete_namespaced_deployment('itoa-knowledge-graph-test-846d9b7bbd-5bs8s', 'itoa')
    # operation.get_one_availabe_node_ip()
    # operation.list_namespaced_pods('itoa')
#查看pod启动是否成功


