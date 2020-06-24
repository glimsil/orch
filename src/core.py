import docker
import time
import os
import copy
from src.modules.storage.services_storage import ServicesStorage
from src.modules.loadbalancer.loadbalancer_storage import LoadBalancerStorage
from src.modules.utils.network_utils import NetworkUtils
from src.providers.container.container_provider_handler import ContainerProviderHandler

class Core:

    client = docker.from_env()
    _container_provider = None
    service_storage = ServicesStorage()
    loadbalancer_storage = LoadBalancerStorage()
    network_utils = NetworkUtils()
    def __init__(self): 
        self._container_provider = ContainerProviderHandler().get_provider()

    #
    # name - string
    # version - string
    # min_replicas - number
    # max_replicas - number
    # autoscale - bool
    # autoscale_strategy - string
    # containers - list
    #
    SERVICE_INFO_TEMPLATE = {
        'name': None,
        'image': None,
        'version': None,
        'min_replicas': 2,
        'max_replicas': 10,
        'autoscale': True,
        'autoscale_strategy': {
            'type' : 'cpu',
            'up' : 50,
            'down' : 10
        },
        'health_uri' : '/'
    } 

    # TODO:
    # Scaling up and down
    # Autoscaling and strategies config.
    # Health check

    def deploy_service(self, service_name, image_name, image_version, lb_port, **kwargs):
        is_new = not self._container_provider.exists_container('traefik_lb_{service_name}'.replace('{service_name}', service_name))
        if(is_new):
            if(lb_port is None):
                lb_port = self.network_utils.get_free_port()
                lb_int_port = self.network_utils.get_free_port()
            self.create_lb(service_name, lb_port, lb_int_port)
            print('Service will listen on port ' + str(lb_port) + '. LB interface on port: ' + str(lb_int_port))
        if(not self.service_storage.service_info_exists(service_name)):
            service_info = self.init_service_info(service_name, image_name, image_version, lb_port)
        else:
            service_info = self.service_storage.get_service_info(service_name)
        self.deploy_scale_service(service_info)

    def deploy_service_with_info(self, service_info):
        service_name = service_info['name']
        #image_name =  service_info['image']
        #image_version =  service_info['version']
        lb_port = service_info.get("port", None)
        lb_int_port = None
        is_new = not self._container_provider.exists_container('traefik_lb_{service_name}'.replace('{service_name}', service_name))
        recreate_lb = False
        if(self.service_storage.service_info_exists(service_name)):
            old_service_info = self.service_storage.get_service_info(service_name)
            comparison = self.compare_service_info(service_info, old_service_info)
            recreate_lb = not comparison['loadbalancer']
        if(is_new):
            if(lb_port is None):
                lb_port = self.network_utils.get_free_port()
                service_info['port'] = lb_port
            if(lb_int_port is None):
                lb_int_port = self.network_utils.get_free_port()
            self.create_lb(service_name, lb_port, lb_int_port)
        elif(recreate_lb):
            self._container_provider.remove_container('traefik_lb_{service_name}'.replace('{service_name}', service_name))
            self.loadbalancer_storage.delete_lb_folder(service_name)
            if(lb_port is None):
                lb_port = self.network_utils.get_free_port()
                service_info['port'] = lb_port
            if(lb_int_port is None):
                lb_int_port = self.network_utils.get_free_port()
            self.create_lb(service_name, lb_port, lb_int_port)
        print('Service listening on port ' + str(lb_port) + '. LB interface on port: ' + str(lb_int_port))
        self.service_storage.save_service_info(service_name, service_info)
        self.deploy_scale_service(service_info)
        
    def init_service_info(self, service_name, image_name, image_version, lb_port):
        service_info = copy.deepcopy(self.SERVICE_INFO_TEMPLATE)
        service_info['name'] = service_name
        service_info['image'] = image_name
        service_info['version'] = image_version
        service_info['port'] = lb_port
        return self.service_storage.save_service_info(service_name, service_info)

    # 
    def compare_service_info(self, new_service_info, old_service_info):
        comparison = {
            'service' : False,
            'loadbalancer': False,
        }
        if(new_service_info['name'] != old_service_info['name']):
            return comparison
        if(new_service_info['port'] == old_service_info['port']):
            comparison['loadbalancer'] = True
        if(new_service_info['image'] == old_service_info['image'] and new_service_info['version'] == old_service_info['version'] and new_service_info['health_uri'] == old_service_info['health_uri']):
            comparison['loadbalancer'] = True
        return comparison

    def create_lb(self, service_name, service_port, lb_dashboard_port):
        lb_image = 'traefik:1.7'
        self.loadbalancer_storage.create_lb_config(service_name)
        line = 'docker run -d -p {lb_dashboard_port}:8080 -p {service_port}:80 -v {toml}:/etc/traefik/traefik.toml -v /var/run/docker.sock:/var/run/docker.sock --name traefik_lb_{service_name} {lb_image}'.replace('{lb_dashboard_port}', str(lb_dashboard_port)).replace('{service_port}', str(service_port)).replace('{service_name}', service_name).replace('{lb_image}', lb_image).replace('{toml}', self.loadbalancer_storage.get_traefik_toml_path(service_name))
        os.system(line)

    def deploy_scale_service(self, service_info):
        containers = self.list_services_by_name(service_info['name'])
        containers_to_scale = service_info['min_replicas']
        # checking if current number of container is greater than min and lesser than max
        if(len(containers) > containers_to_scale):
            containers_to_scale = len(containers)
            if(containers_to_scale > service_info['max_replicas']):
                containers_to_scale = service_info['max_replicas']
        # creating new containers
        for i in range(containers_to_scale):
            self.deploy_service_instance(service_info)
        
        # removing old ones
        for old_container in containers:
            old_container.remove(force=True)

    def deploy_service_instance(self, service_info):
        image = service_info['image']
        if(service_info['version'] != None):
            image += ':' + str(service_info['version'])
        labels = {
            'orch.service.name' : service_info['name'],
            'traefik.tags' : service_info['name'], 
            'traefik.backend': service_info['name'], 
            'traefik.port' : str(80), 
            'traefik.frontend.rule':'Host:localhost'
            }
        ports = {
            str(service_info['port']) + '/tcp': None
            }
        name = service_info['name'] + '_' + str(round(time.time() * 1000))
        self.client.containers.run(image, detach=True, name = name, labels = labels, ports = ports) 

    def scale_service(self, service_name, scale_to):
        if(self.service_storage.service_info_exists(service_name)):
            service_info = self.service_storage.get_service_info(service_name)
        else:
            print('There is no service info for this service name.')
            return
        if(scale_to > service_info['max_replicas']):
            scale_to = service_info['max_replicas']
        elif(scale_to < service_info['min_replicas']):
            scale_to = service_info['min_replicas']
        containers = self.list_services_by_name(service_name)
        if(len(containers) == scale_to):
            print('Same number of replicas as requested. No changes on service.')
        elif(len(containers) < scale_to):
            print('Scaling up to ' + str(scale_to))
            for i in range(scale_to - len(containers)):
                self.scale_service_up(service_name, service_info)
        else:
            print('Scaling down to ' + str(scale_to))
            for i in range(len(containers) - scale_to):
                self.scale_service_down(service_name, service_info)
    
    def scale_service_up(self, service_name, service_info=None):
        if(service_info == None):
            if(self.service_storage.service_info_exists(service_name)):
                service_info = self.service_storage.get_service_info(service_name)
            else:
                print('There is no service info for this service name.')
                return
        
        containers = self.list_services_by_name(service_name)
        if(service_info['max_replicas'] > len(containers)):
            print('Scaling up ' + service_name)
            self.deploy_service_instance(service_info)
        else:
            print('Service \'' + service_name + '\' exceeded the max replicas limit.')

    def scale_service_down(self, service_name, service_info=None):
        if(service_info == None):
            if(self.service_storage.service_info_exists(service_name)):
                service_info = self.service_storage.get_service_info(service_name)
            else:
                print('There is no service info for this service name.')
                return
        
        containers = self.list_services_by_name(service_name)
        if(service_info['min_replicas'] < len(containers)):
            print('Scaling down ' + service_name)
            containers[-1].remove(force=True)
        else:
            print('Service \'' + service_name + '\' exceeded the min replicas limit.')

    def remove_service(self, service_name):
        self._container_provider.remove_container('traefik_lb_{service_name}'.replace('{service_name}', service_name))
        containers = self.list_services_by_name(service_name)
        for container in containers:
            container.remove(force=True)
        self.service_storage.delete_service_info(service_name)
        self.loadbalancer_storage.delete_lb_folder(service_name)

    def count_services_by_name(self, service_name):
        containers = self.list_services_by_name(service_name)
        return len(containers)

    def list_services_by_name(self, service_name):
        params = {
            'filters': {'label' : 'orch.service.name='+service_name}
        }
        return self._container_provider.list_containers(params)
        
    def get_container_provider(self):
        return self._container_provider

