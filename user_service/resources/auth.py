from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_restful import reqparse, Resource
from user_service.models import User as UserModel


class UserAuth(Resource):
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
        return user

    def post(self):
        args = self.parser.parse_args()
        user = self.user_exists(args['username'])
        if user is None:
            return {'error': f'User {args["username"]} does not exist.'}, 404
        if not user.verify_password(args['password']):
            return {
                'error': f'Invalid password for user {args["username"]}.'
            }, 401
        access_token = create_access_token(identity=user.user_id)
        return {'access_token': access_token}, 200
    
    @jwt_required
    def get(self):
        try:
            current_user = get_jwt_identity()
            return {'username': current_user}, 200
        except Exception as e:
            return {'error': f'{e}'}, 500
