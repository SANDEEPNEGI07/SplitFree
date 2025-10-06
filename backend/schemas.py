from marshmallow import Schema, fields
from datetime import datetime as dt

# User related Schema
class UserSchema(Schema):
    """User must have these details"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    class Meta:
        ordered = True
        # password is load_only; on dump you'll see id, username, email in this order
        fields = ("id", "username", "email", "password")

class UserLoginSchema(Schema):
    """Schema for user login - requires email for authentication"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserIdSchema(Schema):
    """This Schema give output to the client"""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()

class GroupMemberSchema(UserIdSchema):
    """This Schema includes user info with admin status for group members"""
    is_admin = fields.Bool(dump_only=True)

class UserIdInputSchema(Schema):
    """This Schema takes input from the client"""
    user_id = fields.Int(required=True)

# Group realted Schema
class GroupCreateSchema(Schema):
    """This Group schema will create groups"""
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    is_public = fields.Bool(load_default=True)

class GroupSchema(GroupCreateSchema):
    """This Group Schema will add the users to the Group"""
    id = fields.Int(dump_only=True)
    invite_code = fields.Str(dump_only=True)
    is_public = fields.Bool(dump_only=True)
    users = fields.List(fields.Nested(UserIdSchema), dump_only=True)

    class Meta:
        ordered = True
        fields = ("id", "name", "description", "invite_code", "is_public", "users")

class GroupInviteEmailSchema(Schema):
    """Schema for sending email invitations to join a group"""
    email = fields.Email(required=True)
    message = fields.Str(load_default="", allow_none=True)  # Optional personal message

class GroupJoinByCodeSchema(Schema):
    """Schema for joining a group using invite code"""
    invite_code = fields.Str(required=True)

class GroupInvitationSchema(Schema):
    """Schema for group invitation details"""
    id = fields.Int(dump_only=True)
    email = fields.Email(dump_only=True)
    invite_token = fields.Str(dump_only=True)
    expires_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    used_at = fields.DateTime(dump_only=True, allow_none=True)
    is_expired = fields.Bool(dump_only=True)
    is_used = fields.Bool(dump_only=True)
    is_valid = fields.Bool(dump_only=True)
    invited_by = fields.Nested(UserIdSchema, dump_only=True)

class GroupCodeInfoSchema(Schema):
    """Schema for group information when looking up by code"""
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    invite_code = fields.Str(dump_only=True)
    member_count = fields.Int(dump_only=True)
    is_public = fields.Bool(dump_only=True)

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
