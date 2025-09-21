from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from models import SettlementModel, GroupModel, UserModel, ExpenseSplitModel, ExpenseModel
from schemas import SettlementSchema, SettlementCreateSchema, BalanceSchema

blp = Blueprint("Settlement", __name__, description="Operations on settlements")

@blp.route("/group/<int:group_id>/settlement")
class GroupSettlement(MethodView):

    @jwt_required
    @blp.arguments(SettlementCreateSchema)
    @blp.response(201, SettlementSchema)
    def post(self, settlement_data, group_id):
        """
        Create a settlement between two users in a group.
        
        Records a payment from one group member to another to settle debts.
        Both users must be members of the group and amount must be positive.
        Users cannot settle with themselves.
        
        Args:
            settlement_data: JSON with amount, paid_by, and paid_to user IDs
            group_id: ID of the group where settlement occurs
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            201: Created settlement object
            400: Error if users are same or amount is not positive
            403: Error if users are not group members
            404: Error if group not found
            401: Error if token is invalid
            500: Error if database operation fails
        """
        group = GroupModel.query.get_or_404(group_id)

        paid_by = settlement_data["paid_by"]
        paid_to = settlement_data["paid_to"]
        amount = settlement_data["amount"]

        if paid_by == paid_to:
            abort(400, message="A user cannot settle with themselves")
        if amount <= 0:
            abort(400, message="Settlement amount must be positive")

        member_ids = {u.id for u in group.users}
        if paid_by not in member_ids or paid_to not in member_ids:
            abort(403, message="Both users must be members of the group")

        settlement = SettlementModel(
            group_id=group_id,
            paid_by=paid_by,
            paid_to=paid_to,
            amount=amount,
        )

        try:
            db.session.add(settlement)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while recording settlement")

        return settlement

    @jwt_required
    @blp.response(200, SettlementSchema(many=True))
    def get(self, group_id):
        """
        Get all settlements in a group.
        
        Retrieves all payment settlements that have been recorded between
        group members to settle shared expenses.
        
        Args:
            group_id: ID of the group to get settlements for
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Array of settlement objects
            404: Error if group not found
            401: Error if token is invalid
        """
        GroupModel.query.get_or_404(group_id)
        return SettlementModel.query.filter_by(group_id=group_id).all()


@blp.route("/group/<int:group_id>/balances")
class GroupBalances(MethodView):

    @jwt_required
    @blp.response(200, BalanceSchema(many=True))
    def get(self, group_id):
        """
        Calculate and get current balances for all group members.
        
        Computes net balances based on expenses and settlements.
        Positive balance means others owe money to this user.
        Negative balance means this user owes money to others.
        
        Args:
            group_id: ID of the group to calculate balances for
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Array of balance objects with user_id, username, and balance
            404: Error if group not found
            401: Error if token is invalid
        """
        group = GroupModel.query.get_or_404(group_id)
        members = group.users
        if not members:
            return []

        balances = _compute_balances(group_id)

        users_by_id = {u.id: u for u in members}
        result = []
        for uid, bal in balances.items():
            user = users_by_id.get(uid)
            if not user:
                continue
            result.append({
                "user_id": uid,
                "username": user.username,
                "balance": float(round(bal, 2))
            })
        return result


def _compute_balances(group_id: int):
    """
    Returns dict: user_id -> net balance
    Positive => others owe this user.
    Negative => this user owes others.
    """
    group = GroupModel.query.get_or_404(group_id)
    member_ids = {u.id for u in group.users}
    balances = {uid: 0.0 for uid in member_ids}

    # All splits for expenses in this group
    splits = (
        ExpenseSplitModel.query
        .join(ExpenseSplitModel.expenses)
        .filter(ExpenseModel.group_id == group_id)
        .all()
    )

    for split in splits:
        payer_id = split.expenses.paid_by
        user_id = split.user_id
        amount = float(split.amount)
        if user_id != payer_id:
            balances[user_id] -= amount
            balances[payer_id] += amount

    # Apply recorded settlements (paid_by receives from paid_to)
    settlements = SettlementModel.query.filter_by(group_id=group_id).all()
    for s in settlements:
        balances[s.paid_by] = balances.get(s.paid_by, 0.0) + float(s.amount)
        balances[s.paid_to] = balances.get(s.paid_to, 0.0) - float(s.amount)

    return balances