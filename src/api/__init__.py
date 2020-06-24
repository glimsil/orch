from flask import Blueprint
from src.core import Core
api = Blueprint('api', __name__)
core = Core()

from src.api.v1.service_api import *
from src.api.v1.node_api import *