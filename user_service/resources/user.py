from flask_restful import reqparse, Resource

from user_service.models import User as UserModel
from user_service.schemas.user import UserSchema


class User(Resource):
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return UserSchema.dump(user)
        return {'error': 'User not found'}
