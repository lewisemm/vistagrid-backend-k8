from flask_jwt_extended import JWTManager
from flask_restful import Api

from user_service.application import app
from user_service.resources.user import User as UserResource, UserList
from user_service.resources.auth import UserAuth

api = Api(app)
jwt = JWTManager(app)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


api.add_resource(UserAuth, '/api/user/auth')
api.add_resource(UserResource, '/api/user/<int:user_id>')
api.add_resource(UserList, '/api/user')
