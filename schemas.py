from marshmallow import Schema, fields
from datetime import datetime as dt

# User related Schema
class UserSchema(Schema):
    """User must have these details"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    class Meta:
        ordered = True
        # password is load_only; on dump you'll see id, username in this order
        fields = ("id", "username", "password")

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
    id = fields.Int(dump_only=True)
    users = fields.List(fields.Nested(UserIdSchema), dump_only=True)

    class Meta:
        ordered = True
        fields = ("id", "name", "description", "users")

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

# Settlement realted schemas
class SettlementCreateSchema(Schema):
    amount = fields.Float(required=True)
    paid_by = fields.Int(required=True)
    paid_to = fields.Int(required=True)

class SettlementSchema(SettlementCreateSchema):
    id = fields.Int(dump_only=True)
    group_id = fields.Int(required=True)

    class Meta:
        ordered = True
        fields = ("id", "group_id", "amount", "paid_by", "paid_to")

class BalanceSchema(Schema):
    user_id = fields.Int()
    username = fields.Str()
    balance = fields.Float()

# Expense history schemas
class ExpenseHistorySplitSchema(Schema):
    user_id = fields.Int(required=True)
    owed = fields.Float(required=True)
    paid = fields.Float(required=True)
    remaining = fields.Float(required=True)

class ExpenseHistoryItemSchema(Schema):
    id = fields.Int(required=True)
    description = fields.Str(required=True)
    amount = fields.Float(required=True)
    date = fields.Date(allow_none=True)
    paid_by = fields.Int(required=True)
    group_id = fields.Int(required=True)
    splits = fields.List(fields.Nested(ExpenseHistorySplitSchema), required=True)

    class Meta:
        ordered = True
        fields = ("id", "description", "amount", "date", "paid_by", "group_id", "splits")

class SettlementHistoryItemSchema(Schema):
    id = fields.Int(required=True)
    type = fields.Str(required=True)  # "settlement"
    amount = fields.Float(required=True)
    date = fields.Date(allow_none=True)
    paid_by = fields.Int(required=True)
    paid_to = fields.Int(required=True)
    group_id = fields.Int(required=True)

    class Meta:
        ordered = True
        fields = ("id", "type", "amount", "date", "paid_by", "paid_to", "group_id")

class HistoryItemSchema(Schema):
    # Unified item schema for both expenses and settlements
    id = fields.Int(required=True)
    type = fields.Str(required=True)  # "expense" | "settlement"
    description = fields.Str(allow_none=True)
    amount = fields.Float(required=True)
    date = fields.Date(allow_none=True)
    paid_by = fields.Int(required=True)
    paid_to = fields.Int(allow_none=True)
    group_id = fields.Int(required=True)
    splits = fields.List(fields.Nested(ExpenseHistorySplitSchema), allow_none=True)

    class Meta:
        ordered = True
        fields = ("id", "type", "description", "amount", "date", "paid_by", "paid_to", "group_id", "splits")

class ExpenseHistoryResponseSchema(Schema):
    group_id = fields.Int(required=True)
    items = fields.List(fields.Nested(HistoryItemSchema), required=True)
