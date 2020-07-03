from flask import jsonify
from flask_restful import reqparse, Resource

from user_service.models import User as UserModel, db
from user_service.schemas.user import UserSchema


class User(Resource):
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return UserSchema.dump(user)
        return {'error': 'User not found'}


class UserList(Resource):
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

    def post(self):
        args = self.parser.parse_args()
        if self.user_exists(args['username']):
            return {'error': f'User {args["username"]} already exists.'}, 409
        new_user = UserModel(**args)
        db.session.add(new_user)
        db.session.commit()
        return {'success': f'User {args["username"]} successfully created'}, 201
