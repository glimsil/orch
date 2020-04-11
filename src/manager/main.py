import time
from runners.autoscaling_runner import AutoScalingRunner
from runners.healthcheck_runner import HealthCheckRunner


asRunner = AutoScalingRunner()
hcRunner = HealthCheckRunner()
while True:
    print("main thread here")
    time.sleep(1)