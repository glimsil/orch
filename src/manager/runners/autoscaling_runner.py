import time
import datetime
import threading

class AutoScalingRunner(object):
    def __init__(self, interval=30):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Control Auto Scaling here here
            print(datetime.datetime.now().__str__() + ' : Starting AutoScalingRunner task in the background')

            time.sleep(self.interval)
