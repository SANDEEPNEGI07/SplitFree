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

        # Check for potential duplicate (same description, amount, payer, and date within the same day)
        # This allows similar expenses but prevents accidental double-clicks/submissions
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
        
        print(f"DEBUG: Group membership found: {group_user}")
        if group_user:
            print(f"DEBUG: User {current_user_id} IS a member of group {group_id}")
        else:
            print(f"DEBUG: User {current_user_id} is NOT a member of group {group_id}")
            # Let's check all group memberships for this user
            all_memberships = GroupUserModel.query.filter_by(user_id=current_user_id).all()
            print(f"DEBUG: User {current_user_id} is member of groups: {[m.group_id for m in all_memberships]}")
            # Let's also check all members of this group
            all_group_members = GroupUserModel.query.filter_by(group_id=group_id).all()
            print(f"DEBUG: Group {group_id} has members: {[m.user_id for m in all_group_members]}")
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        group = GroupModel.query.get_or_404(group_id)
        expenses = ExpenseModel.query.filter_by(group_id=group_id).all()
        print(f"DEBUG: Found {len(expenses)} expenses in group {group_id}")
        return expenses
    
@blp.route("/group/<int:group_id>/expense/<int:expense_id>")
class ExpenseDetail(MethodView):

    @jwt_required()
    def delete(self, group_id, expense_id):
        """Delete an expense and warn if settlements may be affected - only if user is a member."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        expense = ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()
        
        # Check if there are any settlements in this group
        settlements_count = SettlementModel.query.filter_by(group_id=group_id).count()
        
        # Delete the expense (cascades to expense splits automatically)
        db.session.delete(expense)
        db.session.commit()
        
        # Provide warning if settlements exist that may now be incorrect
        message = "Expense deleted successfully"
        if settlements_count > 0:
            message += f". Warning: {settlements_count} settlement(s) exist in this group. Consider recalculating balances to ensure settlements are still appropriate."
        
        return {"message": message}, 200

    @jwt_required()
    @blp.response(200, ExpenseSchema)
    def get(self,group_id, expense_id):
        """Get details of a specific expense by ID - only if user is a member."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        return ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()