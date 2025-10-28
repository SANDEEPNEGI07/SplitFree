from datetime import datetime, timedelta
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import ExpenseSchema, ExpenseCreateSchema
from db import db
from models import ExpenseModel, GroupModel, ExpenseSplitModel, SettlementModel, GroupUserModel
from utils.permissions import check_group_membership, check_expense_permission

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):

    @jwt_required()
    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        """Create a new expense in a group."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        check_group_membership(group_id, current_user_id)

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

        split_type = expense_data.get("split_type", "equal")
        custom_splits = expense_data.get("splits", [])

        expense = ExpenseModel(
            description=expense_data["description"],
            amount=expense_data["amount"],
            paid_by=expense_data["paid_by"],
            date=current_date,
            group_id=group_id,
            split_type=split_type
        )

        try:
            db.session.add(expense)
            db.session.flush()

            # Handle different split types
            if split_type == "equal":
                # Equal split among all members
                share = expense.amount / len(users)
                for user in users:
                    split = ExpenseSplitModel(
                        expense_id=expense.id,
                        user_id=user.id,
                        amount=share
                    )
                    db.session.add(split)
            
            elif split_type == "unequal":
                # Unequal split with custom amounts
                if not custom_splits:
                    abort(400, message="Custom splits required for unequal split type")
                
                total_split = sum(s.get("amount", 0) for s in custom_splits)
                if abs(float(total_split) - float(expense.amount)) > 0.01:
                    abort(400, message=f"Split amounts must sum to total expense amount. Got {total_split}, expected {expense.amount}")
                
                for split_data in custom_splits:
                    if split_data["user_id"] not in member_ids:
                        abort(400, message=f"User {split_data['user_id']} is not a member of this group")
                    
                    split = ExpenseSplitModel(
                        expense_id=expense.id,
                        user_id=split_data["user_id"],
                        amount=split_data["amount"]
                    )
                    db.session.add(split)
            
            elif split_type == "percentage":
                # Percentage-based split
                if not custom_splits:
                    abort(400, message="Custom splits required for percentage split type")
                
                total_percentage = sum(s.get("percentage", 0) for s in custom_splits)
                if abs(total_percentage - 100) > 0.01:
                    abort(400, message=f"Percentages must sum to 100. Got {total_percentage}")
                
                for split_data in custom_splits:
                    if split_data["user_id"] not in member_ids:
                        abort(400, message=f"User {split_data['user_id']} is not a member of this group")
                    
                    amount = (split_data["percentage"] / 100) * float(expense.amount)
                    split = ExpenseSplitModel(
                        expense_id=expense.id,
                        user_id=split_data["user_id"],
                        amount=amount
                    )
                    db.session.add(split)
            
            else:
                abort(400, message=f"Invalid split type: {split_type}. Must be 'equal', 'unequal', or 'percentage'")

            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Expense already created")

        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating expense: {str(e)}")

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
        """Delete an expense and warn if settlements may be affected - only if user is admin or expense creator."""
        
        current_user_id = int(get_jwt_identity())
        
        expense = ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()
        
        # Check if user can delete this expense (admin or expense creator)
        check_expense_permission(expense, current_user_id)
        
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
        
        # Check if the user is a member of this group
        check_group_membership(group_id, current_user_id)
        
        return ExpenseModel.query.filter_by(id=expense_id, group_id=group_id).first_or_404()