from flask import jsonify
from api import api
import socket

@api.route('/v1/node/who/i/am', methods=['GET'])
def node_who_i_am():
    return jsonify({'node_name':str(socket.gethostname())})

@api.route('/v1/node/sync', methods=['POST'])
def node_sync():
    return jsonify({'node_name':str(socket.gethostname())})

@api.route('/v1/node/cluster/join', methods=['POST'])
def node_cluster_join():
    return jsonify({'node_name':str(socket.gethostname())})