from marshmallow import Schema, fields

# User related Schema
class UserSchema(Schema):
    """User must have these details"""
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserIdSchema(Schema):
    """This Schema give output to the client"""
    id = fields.Int(dump_only=True)
    username = fields.Str()

class UserIdInputSchema(Schema):
    """This Schema takes input from the client"""
    user_id = fields.Int(required=True)

# Group realted Schema
class GroupCreateSchema(Schema):
    """This Group schema will create groups"""
    name = fields.Str(required=True)
    description = fields.Str(required=True)

class GroupSchema(GroupCreateSchema):
    """This Group Schema will add the users to the Group"""
    id = fields.Str(dump_only=True)
    users = fields.List(fields.Nested(UserIdSchema), dump_only=True)

# Expense realted Schema
class ExpenseCreateSchema(Schema):
    amount = fields.Float(required=True)
    description = fields.Str(required=True)
    paid_by = fields.Int(required=True)
    date = fields.Date(required=False)

class ExpenseSchema(ExpenseCreateSchema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
