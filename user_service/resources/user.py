from flask import jsonify
from flask_restful import reqparse, Resource

from user_service.models import User as UserModel, db
from user_service.schemas.user import UserSchema

USER_NOT_FOUND = {'error': 'User not found'}


class User(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'password',
            type=str,
            help='password field is required.',
            required=True
        )
        self.user_schema = UserSchema()

    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return self.user_schema.dump(user), 200
        return USER_NOT_FOUND, 404

    def put(self, user_id):
        user = UserModel.query.get(user_id)
        args = self.parser.parse_args()
        hashed_password = user.hash_password(args['password'])
        if user:
            user.password = hashed_password or user.password
            db.session.add(user)
            db.session.commit()
            return {'success': 'password successfully updated.'}, 200
        return USER_NOT_FOUND, 404

    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return '', 204
        return USER_NOT_FOUND, 404


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
        return {
            'success': f'User {args["username"]} successfully created'
        }, 201
