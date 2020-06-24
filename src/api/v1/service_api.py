from flask import request, jsonify
from src.api import api, core

@api.route('/v1/service/deploy', methods=['POST'])
def service_deploy():
    service_info = request.json
    core.deploy_service_with_info(service_info)
    return jsonify(core.service_storage.get_service_info(service_info['name']))

@api.route('/v1/service/deploy/<name>', methods=['GET'])
def service_get_deployment(name):
    return jsonify(core.service_storage.get_service_info(name))



