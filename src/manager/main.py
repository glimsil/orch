import time
from manager.runners.autoscaling_runner import AutoScalingRunner
from manager.runners.healthcheck_runner import HealthCheckRunner

import sys
import time

class OrchManager():
    def init(self):
        asRunner = AutoScalingRunner()
        hcRunner = HealthCheckRunner()
        while True:
            print('checking runners')
            time.sleep(30)
