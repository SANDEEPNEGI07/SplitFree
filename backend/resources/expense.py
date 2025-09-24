from datetime import datetime, timedelta
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import ExpenseSchema, ExpenseCreateSchema
from db import db
from models import ExpenseModel, GroupModel, ExpenseSplitModel, SettlementModel, GroupUserModel

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):

    @jwt_required()
    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        """Create a new expense in a group and split it equally among all members - only if user is a member."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")

        group = GroupModel.query.get_or_404(group_id)
        users = group.users

        if not users:
            abort(400, message="No users in this group to split expense.")

        # Validate that paid_by user exists and is in the group
        payer_id = expense_data["paid_by"]
        member_ids = {u.id for u in users}
        if payer_id not in member_ids:
            abort(400, message="Payer must be a member of the group.")

        current_date = expense_data.get("date") or datetime.now().date()
        existing_expense = ExpenseModel.query.filter(
            ExpenseModel.description == expense_data["description"],
            ExpenseModel.amount == expense_data["amount"],
            ExpenseModel.paid_by == expense_data["paid_by"],
            ExpenseModel.group_id == group_id,
            ExpenseModel.date == current_date
        ).first()
        
        if existing_expense:
            abort(409, message="A similar expense was already created today. If this is intentional, please modify the description slightly.")

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
            abort(409, message="Expense already created")

        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating expense")

        return expense
    
    @jwt_required()
    @blp.response(200, ExpenseSchema(many=True))
    def get(self, group_id):
        """Get all expenses in a specific group - only if user is a member."""
        
        # Get the current logged-in user ID
        current_user_id_raw = get_jwt_identity()
        
        try:
            current_user_id = int(current_user_id_raw)
        except (ValueError, TypeError):
            abort(400, message="Invalid user ID in token")
        
        # Check if the user is a member of this group
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        group = GroupModel.query.get_or_404(group_id)
        expenses = ExpenseModel.query.filter_by(group_id=group_id).all()
        return expenses
    
@blp.route("/group/<int:group_id>/expense/<int:expense_id>")
class ExpenseDetail(MethodView):

    @jwt_required()
    def delete(self, group_id, expense_id):
        """Delete an expense and warn if settlements may be affected - only if user is a member."""
        
        current_user_id = int(get_jwt_identity())
        
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        expense = ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()
        
        settlements_count = SettlementModel.query.filter_by(group_id=group_id).count()
        
        db.session.delete(expense)
        db.session.commit()
        
        message = "Expense deleted successfully"
        if settlements_count > 0:
            message += f". Warning: {settlements_count} settlement(s) exist in this group. Consider recalculating balances to ensure settlements are still appropriate."
        
        return {"message": message}, 200

    @jwt_required()
    @blp.response(200, ExpenseSchema)
    def get(self,group_id, expense_id):
        """Get details of a specific expense by ID - only if user is a member."""
        
        current_user_id = int(get_jwt_identity())
        
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        return ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()