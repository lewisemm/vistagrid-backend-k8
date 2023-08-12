from flask import current_app
from flask_restful import reqparse, Resource
from flask_apispec import use_kwargs, marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, get_jwt

from user_service.models import User as UserModel, db
from user_service.schemas.user import UserSchema, PasswordSchema
from user_service.decorators.auth import is_owner
from user_service.decorators.cache import get_redis_connection


class User(MethodResource, Resource):
    """
    FETCH, UPDATE user details, or DELETE a User.
    """
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'password',
            type=str,
            help='password field is required.',
            required=True
        )

    @doc(description='Get user details for User with <user_id>.')
    @marshal_with(UserSchema, code=201)
    @jwt_required()
    @is_owner
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        return UserSchema().dump(user), 200


    @doc(description='Update password for User with <user_id>.')
    @use_kwargs(PasswordSchema, location=('json'))
    @marshal_with(UserSchema, code=200)
    @jwt_required()
    @is_owner
    def put(self, user_id, **kwargs):
        args = self.parser.parse_args()
        user = UserModel.query.get(user_id)
        hashed_password = user.hash_password(args['password'])
        user.password = hashed_password or user.password
        db.session.add(user)
        db.session.commit()
        return {'success': 'password successfully updated.'}, 200

    @doc(description='Delete User of <user_id>.')
    @marshal_with(UserSchema, code=204)
    @jwt_required()
    @get_redis_connection
    @is_owner
    def delete(self, user_id, redis_conn=None):
        user = UserModel.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        jti = get_jwt()['jti']
        ttl = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        redis_conn.get('redis').set(jti, jti, ttl)
        return '', 204


class UserList(MethodResource, Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username',
            type=str,
            help='username field is required.',
            required=True
        )
        self.parser.add_argument(
            'password',
            type=str,
            help='password field is required.',
            required=True
        )

    def user_exists(self, username):
        user = UserModel.query.filter_by(username=username).first()
        return True if user else False

    @doc(description='Create a new user with `username` and `password` data.')
    @use_kwargs(UserSchema, location=('json'))
    @marshal_with(UserSchema, code=201)
    def post(self, **kwargs):
        args = self.parser.parse_args()
        if self.user_exists(args['username']):
            return {'error': f'User {args["username"]} already exists.'}, 409
        new_user = UserModel(**args)
        db.session.add(new_user)
        db.session.commit()
        return UserSchema().dump(new_user), 201
