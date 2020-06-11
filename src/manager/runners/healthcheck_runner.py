import time
import datetime
import threading
import os
import requests
from src.core import Core

class HealthCheckRunner(object):
    _TAG = '[HealthCheckRunner]'
    core = Core()

    INTERNAL_SERVICE_PORT = '80'

    def __init__(self, interval=10):
        print(self._TAG+datetime.datetime.now().__str__() + ' : Starting HealthCheckRunner task in the background')
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Control Health check here
            print(self._TAG+datetime.datetime.now().__str__() + ' : checking services status')
            for service_name in self.core.service_storage.get_services():
                containers = self.core.list_services_by_name(service_name)
                for container in containers:
                    ip = container.attrs['NetworkSettings']['IPAddress']
                    response = requests.get('http://' + str(ip) + ':' + self.INTERNAL_SERVICE_PORT)
                    if(response.status_code in (200, 201, 202, 203, 204, 205)):
                        #print('ok')
                        1+1
                    else:
                        containers.remove(force=True)
                        self.core.scale_service_up(service_name)
            time.sleep(self.interval)
