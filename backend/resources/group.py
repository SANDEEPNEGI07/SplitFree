import uuid
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import GroupSchema, GroupCreateSchema, UserIdInputSchema
from db import db
from models import GroupModel, GroupUserModel, UserModel, SettlementModel, ExpenseModel, ExpenseSplitModel

blp = Blueprint("Group", __name__, description="Operations on group")

@blp.route("/group")
class GroupList(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema(many=True))
    def get(self):
        """Get all groups where the current user is a member."""
    
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Query groups where the current user is a member
        user_groups = db.session.query(GroupModel).join(
            GroupUserModel, GroupModel.id == GroupUserModel.group_id
        ).filter(GroupUserModel.user_id == current_user_id).all()
        
        return user_groups

    @jwt_required()
    @blp.arguments(GroupCreateSchema)
    @blp.response(201, GroupSchema)
    def post(self, group_data):
        """Create a new group and automatically add the creator as first member."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Verify the user exists
        current_user = UserModel.query.get(current_user_id)
        if not current_user:
            abort(404, message="Current user not found")
        
        group = GroupModel(**group_data)
        try:
            db.session.add(group)
            db.session.flush()
            group_user = GroupUserModel(group_id=group.id, user_id=current_user_id)
            db.session.add(group_user)
            
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="A group with that name already exists.")

        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating group.")
        
        return group

    
@blp.route("/group/<int:group_id>")
class Group(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema)
    def get(self, group_id):
        """Get group details by ID including all members - only if user is a member."""
    
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not group_user:
            abort(403, message="Access denied. You are not a member of this group.")
        
        return GroupModel.query.get_or_404(group_id)

    @jwt_required()
    def delete(self, group_id):
        """Delete group permanently. Cannot delete if group has expenses or settlements. Only group members can delete."""
        
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
        
        # Check for constraints that prevent deletion
        constraints = []
        
        # Check if group has any expenses
        expenses_count = group.expenses.count()
        if expenses_count > 0:
            constraints.append(f"has {expenses_count} expense(s)")
        
        # Check if group has any settlements
        settlements_count = group.settlements.count()
        if settlements_count > 0:
            constraints.append(f"has {settlements_count} settlement(s)")
        
        if constraints:
            constraint_text = ", ".join(constraints)
            abort(400, message=f"Cannot delete group. Group {constraint_text}. Please clear all financial activity first.")
        
        db.session.delete(group)
        db.session.commit()

        return {"message":"Group deleted successfully"}, 200
    

@blp.route("/group/<int:group_id>/user")
class UserToGroup(MethodView):

    @jwt_required()
    @blp.arguments(UserIdInputSchema)
    def post(self, user_data, group_id):
        """Add a user to a group by user ID. Only group members can add users."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is a member of this group
        current_user_in_group = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not current_user_in_group:
            abort(403, message="Access denied. You are not a member of this group.")
        
        user_id = user_data.get("user_id") 
        
        # Validate user exists
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message="User not found")
            
        group = GroupModel.query.get(group_id)
        if not group:
            abort(404, message="Group not found")

        # Check if user already in group
        existing = GroupUserModel.query.filter_by(group_id=group_id, user_id=user_id).first()
        if existing:
            abort(400, message="User already in group")

        # Add user to group
        group_user = GroupUserModel(group_id=group_id, user_id=user_id)
        try:
            db.session.add(group_user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while adding user to group.")

        return {"message": f"{user.username} is added to {group.name}"}, 201


@blp.route("/group/<int:group_id>/user/<int:user_id>")
class RemoveUserFromGroup(MethodView):

    @jwt_required()
    def delete(self, group_id, user_id):
        """Remove a user from a group. Prevents removal if user has financial obligations. Only group members can remove users."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is a member of this group
        current_user_in_group = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not current_user_in_group:
            abort(403, message="Access denied. You are not a member of this group.")
        
        group_user = GroupUserModel.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not group_user:
            abort(404, message="User not found in group")
        
        # Check for financial constraints that prevent removal
        constraints = []
        
        # Check if user has paid for any expenses in this group
        paid_expenses = ExpenseModel.query.filter_by(group_id=group_id, paid_by=user_id).count()
        if paid_expenses > 0:
            constraints.append(f"has paid for {paid_expenses} expense(s) in this group")
        
        # Check if user has any expense splits in this group
        user_splits = (ExpenseSplitModel.query
                      .join(ExpenseModel)
                      .filter(ExpenseModel.group_id == group_id, ExpenseSplitModel.user_id == user_id)
                      .count())
        if user_splits > 0:
            constraints.append(f"has {user_splits} expense split(s) in this group")
        
        # Check if user is involved in any settlements in this group
        settlements_as_payer = SettlementModel.query.filter_by(group_id=group_id, paid_by=user_id).count()
        settlements_as_receiver = SettlementModel.query.filter_by(group_id=group_id, paid_to=user_id).count()
        total_settlements = settlements_as_payer + settlements_as_receiver
        if total_settlements > 0:
            constraints.append(f"is involved in {total_settlements} settlement(s) in this group")
        
        if constraints:
            constraint_text = ", ".join(constraints)
            abort(400, message=f"Cannot remove user from group. User {constraint_text}. Please resolve these obligations first.")
        
        db.session.delete(group_user)
        db.session.commit()
        return {"message": "User removed from group successfully"}, 200


