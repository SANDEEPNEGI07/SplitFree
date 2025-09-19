from flask_smorest import Blueprint
from flask.views import MethodView
from sqlalchemy.orm import joinedload

from models import ExpenseModel, ExpenseSplitModel, SettlementModel, GroupModel
from schemas import ExpenseHistoryResponseSchema, ExpenseHistoryItemSchema, SettlementHistoryItemSchema

blp = Blueprint("History", __name__, description="Expense and settlement history")

@blp.route("/group/<int:group_id>/history")
class GroupHistory(MethodView):
    @blp.response(200, ExpenseHistoryResponseSchema)
    def get(self, group_id):
        GroupModel.query.get_or_404(group_id)

        # Load expenses with splits to compute owed/paid/remaining
        expenses = (
            ExpenseModel.query
            .options(joinedload(ExpenseModel.splits))
            .filter(ExpenseModel.group_id == group_id)
            .all()
        )

        expense_items = []
        for e in expenses:
            # owed = per-split amount recorded
            # paid = share for payer (they paid the whole amount, but for history we'll show they "paid" only their share here; net transfer uses balances)
            # remaining = owed - paid
            splits = []
            for s in e.splits:
                owed = float(s.amount)
                paid = owed if s.user_id == e.paid_by else 0.0
                remaining = float(round(owed - paid, 2))
                splits.append({
                    "user_id": s.user_id,
                    "owed": float(round(owed, 2)),
                    "paid": float(round(paid, 2)),
                    "remaining": remaining
                })
            item = {
                "id": e.id,
                "type": "expense",
                "description": e.description,
                "amount": float(e.amount),
                "date": e.date,
                "paid_by": e.paid_by,
                "paid_to": None,
                "group_id": e.group_id,
                "splits": splits
            }
            expense_items.append(item)

        # Settlements as history items
        settlements = SettlementModel.query.filter_by(group_id=group_id).all()
        settlement_items = []
        for s in settlements:
            settlement_items.append({
                "id": s.id,
                "type": "settlement",
                "description": None,
                "amount": float(s.amount),
                "date": None,
                "paid_by": s.paid_by,
                "paid_to": s.paid_to,
                "group_id": s.group_id,
                "splits": None,
            })

        # Combine chronologically if dates exist; settlements have None date so append after expenses
        # If you later add timestamps to settlements, you can sort by that.
        items = expense_items + settlement_items
        return {"group_id": group_id, "items": items}
