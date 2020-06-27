import requests
import json
from src.modules.storage.host_storage import HostStorage

class OrchClient():
    _host_storage = HostStorage()


    DEPLOY_PATH = '/v1/service/deploy'
    GET_SERVICE_PATH = '/v1/service/{{service_name}}'
    REMOVE_PATH = '/v1/service/{{service_name}}'
    SCALE_PATH = '/v1/service/{{service_name}}/scale/{{replicas}}'
    SCALE_UP_PATH = '/v1/service/{{service_name}}/scale-up'
    SCALE_DOWN_PATH = '/v1/service/{{service_name}}/scale-down'

    def __init__(self, host_file_path): 
        if(host_file_path is None):
            self.HOST_FILE = self._host_storage.get_host_file()
        else:
            self.HOST_FILE = self._host_storage.get_host_file(host_file_path)
    
    def deploy_service(self, service_info_file, service_info_raw):
        if(service_info_file is None and service_info_raw is None):
            print('You should inform one of the following fields: service_info_file, service_info_raw')
        if(service_info_file is not None):
            with open(service_info_file, 'r') as f:
                body = json.load(f)
                requests.post('http://{{host}}:{{port}}{{deploy_path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{deploy_path}}', self.DEPLOY_PATH), json=body)
        elif(service_info_raw is not None):
            requests.post('http://{{host}}:{{port}}{{deploy_path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{deploy_path}}', self.DEPLOY_PATH), json=json.loads(service_info_raw))

    def get_service(self, service_name):
        response = requests.get('http://{{host}}:{{port}}{{path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{path}}', self.GET_SERVICE_PATH).replace('{{service_name}}', service_name))
        return response.content

    def remove_service(self, service_name):
        requests.delete('http://{{host}}:{{port}}{{path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{path}}', self.REMOVE_PATH).replace('{{service_name}}', service_name))

    def scale(self, service_name, scale_to):
        requests.post('http://{{host}}:{{port}}{{path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{path}}', self.SCALE_PATH).replace('{{service_name}}', service_name).replace('{{replicas}}', str(scale_to)))

    def scale_up(self, service_name):
        requests.post('http://{{host}}:{{port}}{{path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{path}}', self.SCALE_UP_PATH).replace('{{service_name}}', service_name))

    def scale_down(self, service_name):
        requests.post('http://{{host}}:{{port}}{{path}}'.replace('{{host}}', str(self.HOST_FILE['ip'])).replace('{{port}}', str(self.HOST_FILE['port'])).replace('{{path}}', self.SCALE_DOWN_PATH).replace('{{service_name}}', service_name))
