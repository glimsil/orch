import docker
import os
from src.providers.container.container_provider_interface import ContainerProviderInterface

class DockerContainerProvider(ContainerProviderInterface):

    _client = docker.from_env()

    CPU_MULTIPLICATOR = 1000000000

    def list_containers(self, params):
        if(params is None):
            return self._client.containers.list()
        return self._client.containers.list(filters=params['filters'])

    def get_container(self, params):
        return self._client.containers.get(params['container_name'])

    def run_container(self, image, detach=None, name=None, labels=None, ports=None, mem_limit=None, memswap_limit=None, cpus=None):
        if(mem_limit is not None and memswap_limit is None):
            memswap_limit = mem_limit
        if(cpus is not None):
            cpus = int(self.CPU_MULTIPLICATOR * float(cpus))
        print(cpus)
        return self._client.containers.run(image, detach=detach, name=name, labels=labels, ports = ports, mem_limit = mem_limit, memswap_limit=memswap_limit, nano_cpus=cpus) 

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
    
    def create_lb(self, service_name, service_port, lb_dashboard_port, lb_config_path):
        lb_image = 'traefik:1.7'
        line = 'docker run -d -p {lb_dashboard_port}:8080 -p {service_port}:80 -v {toml}:/etc/traefik/traefik.toml -v /var/run/docker.sock:/var/run/docker.sock --name traefik_lb_{service_name} {lb_image}'.replace('{lb_dashboard_port}', str(lb_dashboard_port)).replace('{service_port}', str(service_port)).replace('{service_name}', service_name).replace('{lb_image}', lb_image).replace('{toml}', lb_config_path)
        os.system(line)
