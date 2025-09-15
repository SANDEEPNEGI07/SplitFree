from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserIdSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()

class UserIdInputSchema(Schema):
    user_id = fields.Int(required=True)

class GroupCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)

class GroupSchema(GroupCreateSchema):
    id = fields.Str(dump_only=True)
    users = fields.List(fields.Nested(UserIdSchema), dump_only=True)

class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    amount = fields.Float(required=True)
    paid_by = fields.Int(required=True)  # user_id of payer
    group_id = fields.Int(required=True)
    date = fields.Date(required=False)
