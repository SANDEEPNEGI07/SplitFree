from marshmallow import Schema, fields
from datetime import datetime as dt

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
class ExpenseSplitSchema(Schema):
    id = fields.Method("get_index", dump_only=True)
    split_id = fields.Int(attribute="id", dump_only=True)
    user_id = fields.Int(required=True)
    amount = fields.Float(dump_only=True)

    def get_index(self, obj):
        try:
            parent = getattr(obj, "expenses", None)
            if parent and parent.splits:
                return parent.splits.index(obj) + 1
        except Exception:
            pass
        return None

class ExpenseCreateSchema(Schema):
    amount = fields.Float(required=True)
    description = fields.Str(required=True)
    paid_by = fields.Int(required=True)
    date = fields.Date(load_default=lambda: dt.now().date())

class ExpenseSchema(ExpenseCreateSchema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)
    splits = fields.List(fields.Nested(ExpenseSplitSchema), dump_only=True)

    class Meta:
        ordered = True
        fields = ("id", "amount", "description", "paid_by", "date", "group_id", "splits")
