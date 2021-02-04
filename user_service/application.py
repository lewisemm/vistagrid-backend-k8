import os
from flask import Flask

app = Flask(__name__)
app.config.from_object(os.environ['USER_SERVICE_CONFIG_MODULE'])
