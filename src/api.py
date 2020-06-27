from flask import Flask
from src.api import api

app = Flask(__name__)
app.register_blueprint(api)
app.run(port=5899)