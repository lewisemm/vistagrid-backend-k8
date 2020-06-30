
from flask_restful import Api

from user_service.application import app
from user_service.resources.user import User as UserResource

api = Api(app)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


api.add_resource(UserResource, '/<int:user_id>')
