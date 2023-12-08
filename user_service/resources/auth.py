from flask_apispec.views import MethodResource
from flask_apispec import use_kwargs, marshal_with, doc
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from flask_restful import reqparse, Resource
from user_service.models import User as UserModel, db
from user_service.schemas.user import UserSchema, TokenSchema
from user_service.decorators.rate_limiter import rate_limit


class UserAuth(MethodResource, Resource):
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
        user = db.session.scalar(
            db.select(UserModel).where(UserModel.username==username)
        )
        return user

    @doc(description='Authenticate a User with `username` and `password` details.')
    @use_kwargs(UserSchema, location=('json'))
    @marshal_with(TokenSchema, code=200)
    @rate_limit('2/15 minutes')
    def post(self, **kwargs):
        args = self.parser.parse_args()
        user = self.user_exists(args['username'])
        if user is None:
            return {'error': f'User {args["username"]} does not exist.'}, 404
        if not user.verify_password(args['password']):
            return {
                'error': f'Invalid password for user {args["username"]}.'
            }, 401
        identity = f'{user.user_id}'
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200

    @doc(description='Get `username` of current authenticated request.')
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            return {'user_id': current_user}, 200
        except Exception as e:
            return {'error': f'{e}'}, 500
