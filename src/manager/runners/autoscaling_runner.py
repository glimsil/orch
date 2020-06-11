import time
import datetime
import threading
import os
from src.core import Core

class AutoScalingRunner(object):
    _TAG = '[AutoScalingRunner]'
    core  = Core()
    def __init__(self, interval=5):
        self.interval = interval
        while True:
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()
            time.sleep(self.interval)

    def run(self):
        print(self._TAG + datetime.datetime.now().__str__() + ' : Starting AutoScalingRunner task in the background')
        
        # Control Auto Scaling here here
        print(self._TAG + datetime.datetime.now().__str__() + ' : Checking services states')
        for service_name in self.core.service_storage.get_services():
            service_info = self.core.service_storage.get_service_info(service_name)
            if (service_info['autoscale']):
                containers = self.core.list_services_by_name(service_name)
                if('autoscale_strategy' in service_info and service_info['autoscale_strategy']['type'] == 'cpu'):
                    #cpu_strategy_thread = threading.Thread(target=self.cpu_check, args=(service_name, containers, service_info))
                    #cpu_strategy_thread.start()
                    self.cpu_check(service_name, containers, service_info)
            else:
                print(self._TAG + datetime.datetime.now().__str__() + ' : autoscaling disabled for service ' + service_name)

            

    def cpu_check(self, service_name, containers, service_info):
        total_cpu_usage = 0
        cpu_sum = 0
        for c in containers:
            app_cpu = os.popen('docker stats --no-stream --format "{{.Name}}:{{.CPUPerc}}" | grep ' + c.name).read()
            cpu = app_cpu.split(':')[1].split('%')[0]
            #print(str(c.name) + ' cpu = ' + str(cpu))
            cpu_sum = cpu_sum + float(cpu)
        total_cpu_usage = cpu_sum/len(containers)
        #print('Total cpu usage for ' + service_name + ', usage = ' + str(total_cpu_usage))
        if(total_cpu_usage > float(service_info['autoscale_strategy']['up'])):
            self.core.scale_service_up(service_name, service_info)
        elif(total_cpu_usage < float(service_info['autoscale_strategy']['down'])):
            self.core.scale_service_down(service_name, service_info)



