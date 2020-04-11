import time
import datetime
import threading
from src.core import Core

class AutoScalingRunner(object):
    core = Core()
    def __init__(self, interval=30):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Control Auto Scaling here here
            print(datetime.datetime.now().__str__() + ' : Starting AutoScalingRunner task in the background')
            for service_name in self.core.service_storage.get_services():
                service_info = self.core.service_storage.get_service_info(service_name)

                containers = self.core.list_services_by_name(service_name)
                for c in containers:
                    print(str(c.name) + ' : ' + str(c.stats(stream=False)))

            time.sleep(self.interval)
