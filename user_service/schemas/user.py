import marshmallow as ma

class UserSchema(ma.Schema):
    username = ma.fields.Str()
    password = ma.fields.Str(load_only=True)


class PasswordSchema(ma.Schema):
    password = ma.fields.Str(required=True)
