import os
from flask import Flask

app = Flask(__name__)

@app.route('/api/image/')
def hello_world():
    return 'Hello, from the Image Service!\n'
