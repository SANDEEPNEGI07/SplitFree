import uuid
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import GroupSchema, GroupCreateSchema, UserIdInputSchema

from db import db

from models import GroupModel, GroupUserModel, UserModel

blp = Blueprint("Group", __name__, description="Operations on group")

@blp.route("/group")
class GroupList(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema(many=True))
    def get(self):
        """
        Get all groups in the system.
        
        Retrieves a list of all available groups with their details
        including group members.
        
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Array of group objects with id, name, description, and users
            401: Error if token is invalid
        """
        return GroupModel.query.all()

    @jwt_required()
    @blp.arguments(GroupCreateSchema)
    @blp.response(201, GroupSchema)
    def post(self, group_data):
        """
        Create a new group.
        
        Creates a new group with name and description. Group starts empty
        and users can be added separately using the add user endpoint.
        
        Args:
            group_data: JSON containing name and description
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            201: Created group object
            400: Error if group name already exists
            401: Error if token is invalid
            500: Error if database operation fails
        """
        group = GroupModel(**group_data)
        try:
            db.session.add(group)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A group with that name already exists.")

        except SQLAlchemyError:
            abort(500, message="An error occured while creating group.")
        
        return group

    
@blp.route("/group/<int:group_id>")
class Group(MethodView):

    @jwt_required()
    @blp.response(200, GroupSchema)
    def get(self, group_id):
        """
        Get group details by ID.
        
        Retrieves detailed information about a specific group including
        all members currently in the group.
        
        Args:
            group_id: Unique identifier of the group
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Group object with id, name, description, and users array
            404: Error if group not found
            401: Error if token is invalid
        """
        return GroupModel.query.get_or_404(group_id)

    @jwt_required()
    def delete(self, group_id):
        """
        Delete group permanently.
        
        Removes the group and all associated data. Group cannot be deleted
        if it has any financial activity (expenses or settlements) as this
        would result in data loss. All financial obligations must be
        settled and cleared before group deletion.
        
        Args:
            group_id: Unique identifier of the group to delete
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming deletion
            400: Error if group has financial activity preventing deletion
            404: Error if group not found
            401: Error if token is invalid
        """
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
        """
        Add a user to a group.
        
        Adds an existing user to a group by their user ID. User must exist
        in the system and cannot already be a member of the group.
        
        Args:
            user_data: JSON containing user_id to add
            group_id: ID of the group to add user to
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            201: Success message with username and group name
            400: Error if user already in group
            404: Error if user or group not found
            401: Error if token is invalid
            500: Error if database operation fails
        """
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
        """
        Remove a user from a group.
        
        Removes a user's membership from a group. Validates that removing
        this user won't leave any invalid settlements. If the user is
        involved in unsettled expenses or active settlements, they cannot
        be removed until those are resolved.
        
        Args:
            group_id: ID of the group to remove user from
            user_id: ID of the user to remove
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming removal
            400: Error if user has unresolved financial obligations
            404: Error if user not found in group
            401: Error if token is invalid
        """
        from models import SettlementModel, ExpenseModel, ExpenseSplitModel
        
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


