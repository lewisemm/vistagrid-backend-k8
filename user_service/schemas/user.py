from flask_marshmallow import Marshmallow

from user_service.application import app

ma = Marshmallow(app)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('username',)
