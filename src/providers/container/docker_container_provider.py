import docker
import os
from src.providers.container.container_provider_interface import ContainerProviderInterface

class DockerContainerProvider(ContainerProviderInterface):

    _client = docker.from_env()

    def list_containers(self, params):
        if(params is None):
            return self._client.containers.list()
        return self._client.containers.list(filters=params['filters'])

    def get_container(self, params):
        return self._client.containers.get(params['container_name'])

    def run_container(self, params):
        return self._client.containers.run(params['image'], detach=params['detach'], name=params['name'], labels=params['labels'], ports = params['ports']) 

    def get_container_cpu_usage(self, identification):
        app_cpu = os.popen('docker stats --no-stream --format "{{.Name}}:{{.CPUPerc}}" | grep ' + identification).read()
        return app_cpu.split(':')[1].split('%')[0]
    
    def exists_container(self, identification):
        exists = False
        try:
            self._client.containers.get(identification)
            exists = True
        except docker.errors.NotFound:
            exists = False
        except docker.errors.APIError as err:
            print("Failed to get lb container: {0}".format(err))
        return exists
    
    def remove_container(self, identification):
        try:
            lb_container = self._client.containers.get(identification)
            lb_container.remove(force=True)
            return True
        except docker.errors.NotFound as err:
            print("Load Balancer Container not found: {0}".format(err))
        except docker.errors.APIError as err:
            print("Failed to get lb container: {0}".format(err))
        return False
