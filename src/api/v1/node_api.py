from flask import jsonify
from src.api import api
import socket

@api.route('/v1/node/who/i/am', methods=['GET'])
def node_who_i_am():
    return jsonify({'node_name':str(socket.gethostname())})