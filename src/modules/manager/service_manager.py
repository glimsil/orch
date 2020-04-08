import json
from pathlib import Path

class ServicesManager:
    SERVICES_FOLDER_PATH = str(Path.home()) +'/.orch/services/'

    def service_exists(self, service_name):
        Path(str(Path.home()) +"/.orch/services").mkdir(parents=True, exist_ok=True)
        return os.path.exists(file_path) and os.stat(file_path).st_size == 0

    def get_service_info(self, service_name):
        Path(str(Path.home()) +"/.orch/services").mkdir(parents=True, exist_ok=True)
        file = open(str(Path.home()) +'/.orch/services/{{service_name}}.json'.replace('service_name', service_name), 'w+')
        return json.load(file)

    