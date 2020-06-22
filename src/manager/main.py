import time
from src.manager.runners.autoscaling_runner import AutoScalingRunner
from src.manager.runners.healthcheck_runner import HealthCheckRunner

import sys
import time

class OrchManager():
    def init(self):
        asRunner = AutoScalingRunner()
        hcRunner = HealthCheckRunner()
        while True:
            print('checking runners')
            time.sleep(30)
