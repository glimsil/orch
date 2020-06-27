import abc

class ContainerProviderInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def list_containers(self, params):
        return
    
    @abc.abstractmethod
    def get_container(self, params):
        return
    
    @abc.abstractmethod
    def run_container(self, image, detach=None, name=None, labels=None, ports=None):
        return
    
    @abc.abstractmethod
    def get_container_cpu_usage(self, identification):
        return
    
    @abc.abstractmethod
    def exists_container(self, identification):
        return

    @abc.abstractmethod
    def remove_container(self, identification):
        return

    @abc.abstractmethod
    def create_lb(self, service_name, service_port, lb_dashboard_port):
        return