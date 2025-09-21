from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import ExpenseSchema, ExpenseCreateSchema
from db import db
from models import ExpenseModel, GroupModel, ExpenseSplitModel

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):

    @jwt_required
    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        """
        Create a new expense in a group.
        
        Records an expense paid by one group member that should be split
        among all group members equally. Automatically creates expense
        splits for each group member.
        
        Args:
            expense_data: JSON with amount, description, paid_by, and optional date
            group_id: ID of the group where expense occurred
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            201: Created expense object with splits
            400: Error if no users in group, payer not in group, or expense exists
            404: Error if group not found
            401: Error if token is invalid
            500: Error if database operation fails
        """

        group = GroupModel.query.get_or_404(group_id)
        users = group.users

        if not users:
            abort(400, message="No users in this group to split expense.")

        # Validate that paid_by user exists and is in the group
        payer_id = expense_data["paid_by"]
        member_ids = {u.id for u in users}
        if payer_id not in member_ids:
            abort(400, message="Payer must be a member of the group.")

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
            db.session.flush()

            share = expense.amount / len(users)

            for user in users:
                split = ExpenseSplitModel(
                    expense_id = expense.id,
                    user_id = user.id,
                    amount = share
                )
                db.session.add(split)

            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            return {"message":"Expense already created"}

        except SQLAlchemyError:
            db.session.rollback()
            return {"message":"An error occured while creating expense"}

        return expense
    
    @jwt_required
    @blp.response(200, ExpenseSchema(many=True))
    def get(self, group_id):
        """
        Get all expenses in a group.
        
        Retrieves all expenses recorded for a specific group including
        expense details and how each expense was split among members.
        
        Args:
            group_id: ID of the group to get expenses for
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Array of expense objects with splits
            404: Error if group not found
            401: Error if token is invalid
        """
        group = GroupModel.query.get_or_404(group_id)
        return ExpenseModel.query.filter_by(group_id=group_id).all()
    
@blp.route("/group/<int:group_id>/expense/<int:expense_id>")
class ExpenseDetail(MethodView):

    @jwt_required
    def delete(self, group_id, expense_id):
        """
        Delete a specific expense from a group.
        
        Permanently removes an expense and all associated splits.
        This affects group balances and cannot be undone.
        
        Args:
            group_id: ID of the group containing the expense
            expense_id: ID of the expense to delete
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming deletion
            404: Error if expense not found in group
            401: Error if token is invalid
        """
        expense = ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()

        db.session.delete(expense)
        db.session.commit()

        return {"message":"Expense deleted successfully"}, 200

    @jwt_required
    @blp.response(200, ExpenseSchema)
    def get(self,group_id, expense_id):
        """
        Get details of a specific expense.
        
        Retrieves detailed information about a single expense including
        how it was split among group members.
        
        Args:
            group_id: ID of the group containing the expense
            expense_id: ID of the expense to retrieve
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Expense object with splits
            404: Error if expense not found in group
            401: Error if token is invalid
        """
        return ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()