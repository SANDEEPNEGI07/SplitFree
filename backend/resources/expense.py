from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import ExpenseSchema, ExpenseCreateSchema
from db import db
from models import ExpenseModel, GroupModel, ExpenseSplitModel, SettlementModel

blp = Blueprint("Expense", __name__, description="Operations on expenses")

@blp.route("/group/<int:group_id>/expense")
class GroupExpense(MethodView):

    @jwt_required()
    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data, group_id):
        """Create a new expense in a group and split it equally among all members - only if user is a member."""
        from flask_jwt_extended import get_jwt_identity
        from models import GroupUserModel
        
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
    
    @jwt_required()
    @blp.response(200, ExpenseSchema(many=True))
    def get(self, group_id):
        """Get all expenses in a specific group - only if user is a member."""
        from flask_jwt_extended import get_jwt_identity
        from models import GroupUserModel
        
        # Get the current logged-in user ID
        current_user_id_raw = get_jwt_identity()
        print(f"DEBUG: Raw JWT identity: {current_user_id_raw} (type: {type(current_user_id_raw)})")
        
        try:
            current_user_id = int(current_user_id_raw)
            print(f"DEBUG: Converted user ID: {current_user_id}")
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Error converting user ID: {e}")
            abort(400, message="Invalid user ID in token")
        
        print(f"DEBUG: User {current_user_id} trying to access expenses for group {group_id}")
        
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
        from flask_jwt_extended import get_jwt_identity
        from models import GroupUserModel
        
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
        from flask_jwt_extended import get_jwt_identity
        from models import GroupUserModel
        
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