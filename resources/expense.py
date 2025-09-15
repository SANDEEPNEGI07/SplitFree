from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import ExpenseSchema, ExpenseCreateSchema
from db import db
from models import ExpenseModel, GroupModel

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):

    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        """Create a new expense in a group"""

        group = GroupModel.query.get_or_404(group_id)

        existing_expense = ExpenseModel.query.filter_by(
            description=expense_data["description"],
            amount=expense_data["amount"],
            paid_by=expense_data["paid_by"],
            group_id=group_id,
            date=expense_data.get("date")
        ).first()
        
        if existing_expense:
            abort(400, message="This expense already exists")

        expense = ExpenseModel(**expense_data, group_id=group_id)

        try:
            db.session.add(expense)
            db.session.commit()
        
        except IntegrityError:
            return {"message":"Expense already created"}

        except SQLAlchemyError:
            return {"message":"An error occured while creating expense"}

        return expense
    
    @blp.response(201, ExpenseSchema(many=True))
    def get(self, group_id):
        """Get all expenses in a group"""
        group = GroupModel.query.get_or_404(group_id)
        return ExpenseModel.query.filter_by(group_id=group_id).all()
    
@blp.route("/group/<int:group_id>/expense/<int:expense_id>")
class ExpenseDetail(MethodView):

    def delete(self, group_id, expense_id):
        """Delete a particular expense from a group"""
        expense = ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()

        db.session.delete(expense)
        db.session.commit()

        return {"message":"Expense deleted successfully"}

    @blp.response(201, ExpenseSchema)
    def get(self,group_id, expense_id):
        """Get a single expense from a group"""
        return ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()