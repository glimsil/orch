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
        Path(self.SERVICES_FOLDER_PATH + service_name).mkdir(parents=True, exist_ok=True)
        os.system("cp $PWD/src/config/traefik.toml " + self.SERVICES_FOLDER_PATH+service_name+"/traefik.toml")
        os.system("sed -i 's/{tag_name}/"+service_name+"/g' " + self.SERVICES_FOLDER_PATH+service_name+"/traefik.toml")
    
    def delete_lb_folder(self, service_name):
        if(self.service_info_exists(service_name)):
            os.system("rm -rf " + self.SERVICES_FOLDER_PATH + service_name)
