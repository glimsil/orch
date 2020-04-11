import os
for file in os.listdir("/home/ilegra0408/.orch/services"):
    if file.endswith(".json"):
        print(file.split('.')[0])