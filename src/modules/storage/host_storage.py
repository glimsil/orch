import json
import os
from pathlib import Path

class HostStorage:
    HOST_FOLDER_PATH = str(Path.home()) +'/.orch/host/'
    DEFAULT_HOST_FILE_NAME = "default_host"
    DEFAULT_HOST_CONFIG = {
        'ip': 'localhost',
        'port': 5899
    }
    def host_file_exists(self, host_file_name=DEFAULT_HOST_FILE_NAME):
        Path(self.HOST_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
        file_path = self.HOST_FOLDER_PATH + '{{host_file_name}}.json'.replace('{{host_file_name}}', host_file_name)
        return os.path.exists(file_path)

    def get_host_file(self, host_file_name=DEFAULT_HOST_FILE_NAME):
        if(not self.host_file_exists(host_file_name)):
            if(host_file_name == self.DEFAULT_HOST_FILE_NAME):
                return self.save_host_file(self.DEFAULT_HOST_CONFIG)
            else:
                return {}
        file_path = self.HOST_FOLDER_PATH + '{{host_file_name}}.json'.replace('{{host_file_name}}', host_file_name)
        with open(file_path, 'r') as file:
            return json.load(file)
    
    def save_host_file(self, data, host_file_name=DEFAULT_HOST_FILE_NAME):
        Path(self.HOST_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
        file_path = self.HOST_FOLDER_PATH + '{{host_file_name}}.json'.replace('{{host_file_name}}', host_file_name)
        with open(file_path, 'w+') as file:
            json.dump(data, file)
        return data
    
    def delete_host_file(self, host_file_name=DEFAULT_HOST_FILE_NAME):
        if(self.host_file_exists(host_file_name)):
            os.remove(self.HOST_FOLDER_PATH + '{{host_file_name}}.json'.replace('{{host_file_name}}', host_file_name))

