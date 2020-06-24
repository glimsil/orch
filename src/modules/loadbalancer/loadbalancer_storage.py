import json
import os
from pathlib import Path

class LoadBalancerStorage:
    SERVICES_FOLDER_PATH = str(Path.home()) +'/.orch/loadbalancer/'

    def service_info_exists(self, service_name):
        return os.path.exists(self.SERVICES_FOLDER_PATH + service_name)


    def get_traefik_toml_path(self, service_name):
        Path(self.SERVICES_FOLDER_PATH + service_name).mkdir(parents=True, exist_ok=True)
        return self.SERVICES_FOLDER_PATH+service_name+"/traefik.toml"

    def create_lb_config(self, service_name):
        current_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(current_path, "../../config/traefik.toml")
        Path(self.SERVICES_FOLDER_PATH + service_name).mkdir(parents=True, exist_ok=True)
        os.system("cp " + str(config_path) + " " + self.SERVICES_FOLDER_PATH+service_name+"/traefik.toml")
        os.system("sed -i 's/{tag_name}/"+service_name+"/g' " + self.SERVICES_FOLDER_PATH+service_name+"/traefik.toml")
    
    def delete_lb_folder(self, service_name):
        if(self.service_info_exists(service_name)):
            os.system("rm -rf " + self.SERVICES_FOLDER_PATH + service_name)
