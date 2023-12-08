import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, current_app, g
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import (
    JWTManager, get_jwt, jwt_required, get_jwt_identity, create_access_token
)
from flask_restful import Api
from flask_migrate import Migrate

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from user_service.resources.user import User as UserResource, UserList
from user_service.resources.auth import UserAuth
from user_service.decorators.cache import get_redis_connection
from user_service.decorators.rate_limiter import rate_limit


def create_app(test_config=False):
    app = Flask(__name__)
    if test_config:
        app.config.from_object('user_service.config.test.TestConfig')
    else:
        app.config.from_object(os.environ['USER_SERVICE_CONFIG_MODULE'])

    limiter = Limiter(
        get_remote_address,
        app=app,
        # set this to prod appropriate url via environment variable or config class
        storage_uri="memory://",
    )
    @app.before_request
    def set_limiter():
        g.limiter = limiter

    from user_service.models import db

    with app.app_context():
        db.init_app(app)
        migrate = Migrate(app, db)
        db.create_all()
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

    @jwt.token_in_blocklist_loader
    @get_redis_connection
    def check_if_token_revoked(jwt_header, jwt_payload, redis_conn=None):
        jti = jwt_payload["jti"]
        token_in_redis = redis_conn.get('redis').get(jti)
        return token_in_redis is not None


    @app.route('/api/user/logout', methods=['POST'])
    @jwt_required(verify_type=False)
    @get_redis_connection
    def api_user_logout(redis_conn=None):
        # The client needs to send two requests to this endpoint.
        # One request to revoke the access token.
        # The other request to revoke the refresh token.
        token = get_jwt()
        jti = token['jti']
        token_type = token['type']
        ttl = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        redis_conn.get('redis').set(jti, jti, ttl)
        message = f'{token_type.capitalize()} token successfully revoked.'
        return { 'message': message }, 200

    @app.route('/api/token/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    @rate_limit('2/15 minutes')
    def refresh():
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return { 'access_token': access_token }, 200


    api.add_resource(UserAuth, '/api/user/auth', endpoint='user-auth')
    api.add_resource(UserResource, '/api/user/<int:user_id>', endpoint='user-detail')
    api.add_resource(UserList, '/api/user', endpoint='user-list')

    docs.register(UserResource, endpoint='user-detail')
    docs.register(UserList, endpoint='user-list')
    docs.register(UserAuth, endpoint='user-auth')

    return app
