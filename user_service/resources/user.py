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

    def post(self):
        args = self.parser.parse_args()
        new_user = UserModel(**args)
        db.session.add(new_user)
        db.session.commit()
        return 'made', 201
