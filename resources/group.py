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

    @jwt_required
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

    @jwt_required
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

    @jwt_required
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

    @jwt_required
    def delete(self, group_id):
        """
        Delete group permanently.
        
        Removes the group and all associated data including expenses,
        settlements, and member relationships. This action cannot be undone.
        
        Args:
            group_id: Unique identifier of the group to delete
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming deletion
            404: Error if group not found
            401: Error if token is invalid
        """
        group = GroupModel.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()

        return {"message":"Group deleted"}, 200
    

@blp.route("/group/<int:group_id>/user")
class UserToGroup(MethodView):

    @jwt_required
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

    @jwt_required
    def delete(self, group_id, user_id):
        """
        Remove a user from a group.
        
        Removes a user's membership from a group. This does not delete
        the user's historical data (expenses, settlements) but prevents
        them from participating in new group activities.
        
        Args:
            group_id: ID of the group to remove user from
            user_id: ID of the user to remove
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming removal
            404: Error if user not found in group
            401: Error if token is invalid
        """
        group_user = GroupUserModel.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not group_user:
            abort(404, message="User not found in group")
        db.session.delete(group_user)
        db.session.commit()
        return {"message": "User removed from group"}, 200


