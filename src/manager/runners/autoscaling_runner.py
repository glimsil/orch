import time
import datetime
import threading
import os
from src.core import Core
from src.providers.container.container_provider_handler import ContainerProviderHandler

class AutoScalingRunner(object):
    _TAG = '[AutoScalingRunner]'
    core = Core()
    _container_provider = None
    def __init__(self, interval=5):
        self._container_provider = ContainerProviderHandler().get_provider()
        self.interval = interval
        while True:
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()
            time.sleep(self.interval)

    def run(self):
        print(self._TAG + datetime.datetime.now().__str__() + ' : Checking services states')
        for service_name in self.core.service_storage.get_services():
            service_info = self.core.service_storage.get_service_info(service_name)
            if (service_info['autoscale']):
                containers = self.core.list_services_by_name(service_name)
                if('autoscale_strategy' in service_info and service_info['autoscale_strategy']['type'] == 'cpu'):
                    self.cpu_check(service_name, containers, service_info)
            else:
                print(self._TAG + datetime.datetime.now().__str__() + ' : autoscaling disabled for service ' + service_name)

            

    def cpu_check(self, service_name, containers, service_info):
        total_cpu_usage = 0
        cpu_sum = 0
        for c in containers:
            cpu = self._container_provider.get_container_cpu_usage(c.name)
            print(c.name + " : " + cpu)
            cpu_sum = cpu_sum + float(cpu)
        if(len(containers) == 0): 
            # if service file exists, but there is no container up #
            self.core.deploy_service(service_name, service_info['image'], service_info['version'], service_info['port'])
        else:
            total_cpu_usage = cpu_sum/len(containers)
        if(total_cpu_usage > float(service_info['autoscale_strategy']['up'])):
            self.core.scale_service_up(service_name, service_info)
        elif(total_cpu_usage < float(service_info['autoscale_strategy']['down'])):
            self.core.scale_service_down(service_name, service_info)



