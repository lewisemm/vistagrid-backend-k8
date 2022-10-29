from flask import jsonify
from flask_restful import reqparse, Resource
from flask_apispec import use_kwargs, marshal_with, doc
from flask_apispec.views import MethodResource

from user_service.models import User as UserModel, db
from user_service.schemas.user import UserSchema, PasswordSchema

USER_NOT_FOUND = {'error': 'User not found'}


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
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return UserSchema().dump(user), 200
        return USER_NOT_FOUND, 404

    @doc(description='Update password for User with <user_id>.')
    @use_kwargs(PasswordSchema, location=('json'))
    @marshal_with(UserSchema, code=200)
    def put(self, user_id, **kwargs):
        args = self.parser.parse_args()
        user = UserModel.query.get(user_id)
        if user:
            hashed_password = user.hash_password(args['password'])
            user.password = hashed_password or user.password
            db.session.add(user)
            db.session.commit()
            return {'success': 'password successfully updated.'}, 200
        return USER_NOT_FOUND, 404

    @doc(description='Delete User with <user_id>.')
    @marshal_with(UserSchema, code=204)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        return USER_NOT_FOUND, 404


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
