import json
import os
from pathlib import Path

class ServicesManager:
    SERVICES_FOLDER_PATH = str(Path.home()) +'/.orch/services/'

    def service_info_exists(self, service_name):
        Path(self.SERVICES_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
        file_path = self.SERVICES_FOLDER_PATH + '{{service_name}}.json'.replace('{{service_name}}', service_name)
        return os.path.exists(file_path)

    def get_service_info(self, service_name):
        if(not self.service_info_exists(service_name)):
            return {}
        file_path = self.SERVICES_FOLDER_PATH + '{{service_name}}.json'.replace('{{service_name}}', service_name)
        with open(file_path, 'r') as file:
            return json.load(file)
    
    def save_service_info(self, service_name, data):
        Path(self.SERVICES_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
        file_path = self.SERVICES_FOLDER_PATH + '{{service_name}}.json'.replace('{{service_name}}', service_name)
        with open(file_path, 'w+') as file:
            json.dump(data, file)
        return data
    
    def delete_service_info(self, service_name):
        if(self.service_info_exists(service_name)):
            os.remove(self.SERVICES_FOLDER_PATH + '{{service_name}}.json'.replace('{{service_name}}', service_name))

