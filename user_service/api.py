import os
import redis

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
redis_conn = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    decode_responses=True
)


@app.route('/')
def hello_world():
    return 'Hello, World!\n'


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = redis_conn.get(jti)
    return token_in_redis is not None


api.add_resource(UserAuth, '/api/user/auth', endpoint='user-auth')
api.add_resource(UserResource, '/api/user/<int:user_id>', endpoint='user-detail')
api.add_resource(UserList, '/api/user', endpoint='user-list')

docs.register(UserResource, endpoint='user-detail')
docs.register(UserList, endpoint='user-list')
docs.register(UserAuth, endpoint='user-auth')
