from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from schemas import ExpenseSchema
from db import db
from models import ExpenseModel, GroupModel

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/expense")
class Expense(MethodView):
    @blp.arguments(ExpenseSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data):
        expense = ExpenseModel(**expense_data)
        try:
            db.session.add(expense)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating expense.")
        return expense, 201

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):
    @blp.arguments(ExpenseSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        group = GroupModel.query.get_or_404(group_id)
        users = group.users
        num_users = len(users)
        if num_users == 0:
            abort(400, message="No users in group to split expense.")

        share = expense_data["amount"] / num_users

        expense = ExpenseModel(
            description=expense_data["description"],
            amount=expense_data["amount"],
            paid_by=expense_data["paid_by"],
            group_id=group_id,
            date=expense_data.get("date")
        )
        db.session.add(expense)
        db.session.commit()

        # Optionally, create a record for each user's share
        split_info = []
        for user in users:
            split_info.append({
                "user_id": user.id,
                "username": user.username,
                "share": share,
                "owes": user.id != expense_data["paid_by"]
            })

        return {
            "expense": ExpenseSchema().dump(expense),
            "split": split_info
        }, 201