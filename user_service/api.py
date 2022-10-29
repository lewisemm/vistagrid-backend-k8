from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager
from flask_restful import Api

from user_service.application import app
from user_service.resources.user import User as UserResource, UserList
from user_service.resources.auth import UserAuth

api = Api(app)
jwt = JWTManager(app)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='User Service API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
})
docs = FlaskApiSpec(app)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


api.add_resource(UserAuth, '/api/user/auth')
api.add_resource(UserResource, '/api/user/<int:user_id>')
api.add_resource(UserList, '/api/user')

docs.register(UserResource)
docs.register(UserList)
