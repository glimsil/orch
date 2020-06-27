from flask import request, jsonify
from src.api import api, core

@api.route('/v1/service/deploy', methods=['POST'])
def service_deploy():
    service_info = request.json
    print(service_info)
    core.deploy_service_with_info(service_info)
    return jsonify(core.service_storage.get_service_info(service_info['name']))

@api.route('/v1/service/<name>', methods=['DELETE'])
def delete_service(name):
    response = {
        'service_name' : name,
        'removed' : True
    }
    try:
        core.remove_service(name)
    except:
        response['removed'] = False
    return jsonify(response)

@api.route('/v1/service/<name>', methods=['GET'])
def service_get_deployment(name):
    return jsonify(core.service_storage.get_service_info(name))

@api.route('/v1/service/<name>/scale/<replicas>', methods=['POST'])
def service_scale(name, replicas):
    return jsonify(core.scale_service(name, replicas))

@api.route('/v1/service/<name>/scale-up', methods=['POST'])
def service_scale_up(name):
    return jsonify(core.scale_service_up(name))

@api.route('/v1/service/<name>/scale-down', methods=['POST'])
def service_scale_down(name):
    return jsonify(core.scale_service_up(name))


