from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserIdSchema(Schema):
    user_id = fields.Str(required=True)

class PlainGroupSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)

class GroupSchema(PlainGroupSchema):
    users = fields.List(fields.Nested(UserSchema))
