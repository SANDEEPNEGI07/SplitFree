import uuid
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import (GroupSchema, GroupCreateSchema, UserIdInputSchema, GroupMemberSchema,
                     GroupInviteEmailSchema, GroupJoinByCodeSchema, GroupInvitationSchema, 
                     GroupCodeInfoSchema)
from db import db
from models import (GroupModel, GroupUserModel, UserModel, SettlementModel, ExpenseModel, 
                    ExpenseSplitModel, GroupInvitationModel)
from utils.permissions import check_group_membership, check_group_admin
from resources.settlement import _compute_balances

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
            # Make the group creator an admin
            group_user = GroupUserModel(group_id=group.id, user_id=current_user_id, is_admin=True)
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
        """Get group details by ID including all members with admin status - only if user is a member."""
    
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        check_group_membership(group_id, current_user_id)
        
        return GroupModel.query.get_or_404(group_id)

    @jwt_required()
    def delete(self, group_id):
        """Delete group permanently. Cannot delete if group has expenses or settlements. Only group admins can delete."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is an admin of this group
        check_group_admin(group_id, current_user_id)
        
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
        """Add a user to a group by user ID. Only group admins can add users."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is an admin of this group
        check_group_admin(group_id, current_user_id)
        
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
        """Remove a user from a group. Prevents removal if user has financial obligations. Only group admins can remove users."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is an admin of this group
        check_group_admin(group_id, current_user_id)
        
        group_user = GroupUserModel.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not group_user:
            abort(404, message="User not found in group")
        
        # Check if admin is trying to remove themselves
        if current_user_id == user_id:
            # Check if they are the only member in the group
            total_members = GroupUserModel.query.filter_by(group_id=group_id).count()
            if total_members == 1:
                abort(400, message="Cannot remove yourself from group. You are the only member. Delete the group instead.")
            
            # Check if they are the only admin in the group
            admin_count = GroupUserModel.query.filter_by(group_id=group_id, is_admin=True).count()
            if admin_count == 1 and group_user.is_admin:
                abort(400, message="Cannot remove yourself from group. You are the only admin. Assign another admin first.")
        
        # Check if removing the only admin (when current user is not the one being removed)
        elif group_user.is_admin:
            admin_count = GroupUserModel.query.filter_by(group_id=group_id, is_admin=True).count()
            if admin_count == 1:
                abort(400, message="Cannot remove the only admin from group. Assign another admin first.")
        
        # Check for financial constraints that prevent removal
        try:
            balances = _compute_balances(group_id)
            user_balance = balances.get(user_id, 0.0)
            
            # Allow removal only if balance is zero (within a small tolerance for floating point precision)
            if abs(user_balance) > 0.01:  # More than 1 cent difference
                if user_balance > 0:
                    abort(400, message=f"Cannot remove user from group. User is owed ${user_balance:.2f}. Please settle all balances first.")
                else:
                    abort(400, message=f"Cannot remove user from group. User owes ${abs(user_balance):.2f}. Please settle all balances first.")
        except Exception as e:
            # Fallback to old constraint checking if balance calculation fails
            constraints = []
            
            # Check if user has unsettled expense splits
            user_splits = (ExpenseSplitModel.query
                          .join(ExpenseModel)
                          .filter(ExpenseModel.group_id == group_id, ExpenseSplitModel.user_id == user_id)
                          .count())
            if user_splits > 0:
                constraints.append(f"has {user_splits} unsettled expense split(s)")
            
            if constraints:
                constraint_text = ", ".join(constraints)
                abort(400, message=f"Cannot remove user from group. User {constraint_text}. Please settle all balances first.")
        
        db.session.delete(group_user)
        db.session.commit()
        return {"message": "User removed from group successfully"}, 200


@blp.route("/group/<int:group_id>/members")
class GroupMembers(MethodView):

    @jwt_required()
    @blp.response(200, GroupMemberSchema(many=True))
    def get(self, group_id):
        """Get all group members with their admin status - only if user is a member."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the user is a member of this group
        check_group_membership(group_id, current_user_id)
        
        # Get all group members with admin status
        group_users = db.session.query(
            UserModel.id,
            UserModel.username,
            UserModel.email,
            GroupUserModel.is_admin
        ).join(
            GroupUserModel, UserModel.id == GroupUserModel.user_id
        ).filter(
            GroupUserModel.group_id == group_id
        ).all()
        
        # Convert to dictionary format for serialization
        members = []
        for user_id, username, email, is_admin in group_users:
            members.append({
                'id': user_id,
                'username': username,
                'email': email,
                'is_admin': is_admin
            })
        
        return members


@blp.route("/group/<int:group_id>/admin")
class GroupAdminManagement(MethodView):

    @jwt_required()
    @blp.arguments(UserIdInputSchema)
    def post(self, user_data, group_id):
        """Make a user admin of the group. Only existing group admins can do this."""
        
        # Get the current logged-in user ID
        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is an admin of this group
        check_group_admin(group_id, current_user_id)
        
        user_id = user_data.get("user_id")
        
        # Check if target user is a member of this group
        target_group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=user_id
        ).first()
        
        if not target_group_user:
            abort(404, message="User is not a member of this group")
        
        if target_group_user.is_admin:
            abort(400, message="User is already an admin of this group")
        
        # Make user admin
        target_group_user.is_admin = True
        
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating admin status.")
        
        return {"message": "User has been made admin successfully"}, 200

    @jwt_required()
    @blp.arguments(UserIdInputSchema)
    def delete(self, user_data, group_id):
        """Remove admin privileges from a user. Only existing group admins can do this."""

        current_user_id = int(get_jwt_identity())
        
        # Check if the current user is an admin of this group
        check_group_admin(group_id, current_user_id)
        
        user_id = user_data.get("user_id")
        
        # Prevent user from removing their own admin privileges if they're the only admin
        admin_count = GroupUserModel.query.filter_by(
            group_id=group_id, 
            is_admin=True
        ).count()
        
        if admin_count == 1 and user_id == current_user_id:
            abort(400, message="Cannot remove admin privileges. At least one admin must remain in the group.")
        
        # Check if target user is a member of this group
        target_group_user = GroupUserModel.query.filter_by(
            group_id=group_id, 
            user_id=user_id
        ).first()
        
        if not target_group_user:
            abort(404, message="User is not a member of this group")
        
        if not target_group_user.is_admin:
            abort(400, message="User is not an admin of this group")
        
        # Remove admin privileges
        target_group_user.is_admin = False
        
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating admin status.")
        
        return {"message": "Admin privileges removed successfully"}, 200


@blp.route("/group/<int:group_id>/invite-email")
class GroupEmailInvite(MethodView):
    
    @jwt_required()
    @blp.arguments(GroupInviteEmailSchema)
    @blp.response(201, GroupInvitationSchema)
    def post(self, invitation_data, group_id):
        """Send email invitation to join group"""
        current_user_id = get_jwt_identity()
        
        # Check if user is admin of the group
        if not check_group_admin(current_user_id, group_id):
            abort(403, message="Only group admins can send invitations")
        
        group = GroupModel.query.get_or_404(group_id)
        current_user = UserModel.query.get(current_user_id)
        email = invitation_data["email"].lower().strip()
        
        # Check if user with this email is already a member
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            existing_membership = GroupUserModel.query.filter_by(
                group_id=group_id, user_id=existing_user.id
            ).first()
            if existing_membership:
                abort(400, message="User is already a member of this group")
        
        # Check if there's already a pending invitation for this email
        existing_invitation = GroupInvitationModel.query.filter_by(
            group_id=group_id, email=email
        ).filter(
            GroupInvitationModel.used_at.is_(None),
            GroupInvitationModel.expires_at > db.func.now()
        ).first()
        
        if existing_invitation:
            abort(400, message="There's already a pending invitation for this email")
        
        # Create invitation
        invitation = GroupInvitationModel(
            group_id=group_id,
            email=email,
            invited_by_user_id=current_user_id
        )
        
        db.session.add(invitation)
        
        try:
            db.session.commit()
            
            # Import here to avoid circular imports
            from flask import current_app
            from tasks import send_group_invitation_email
            
            # Get member count
            member_count = GroupUserModel.query.filter_by(group_id=group_id).count()
            
            # Create join URL (frontend will handle the invitation token)
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
            join_url = f"{frontend_url}/invite/{invitation.invite_token}"
            
            # Send invitation email (async if queue available, sync otherwise)
            try:
                if hasattr(current_app, 'queue') and current_app.queue:
                    current_app.queue.enqueue(
                        send_group_invitation_email,
                        email,
                        group.name,
                        group.description,
                        current_user.username,
                        member_count,
                        invitation.invite_token,
                        group.invite_code,
                        invitation.expires_at,
                        join_url
                    )
                else:
                    send_group_invitation_email(
                        email,
                        group.name,
                        group.description,
                        current_user.username,
                        member_count,
                        invitation.invite_token,
                        group.invite_code,
                        invitation.expires_at,
                        join_url
                    )
            except Exception as e:
                current_app.logger.error(f"Failed to send invitation email: {str(e)}")
                # Don't fail the invitation creation if email fails
            
            return invitation, 201
            
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the invitation")


@blp.route("/invite/<string:token>")
class AcceptEmailInvite(MethodView):
    
    @jwt_required()
    def get(self, token):
        """Accept group invitation via email token"""
        current_user_id = get_jwt_identity()
        current_user = UserModel.query.get(current_user_id)
        
        # Find the invitation
        invitation = GroupInvitationModel.query.filter_by(invite_token=token).first()
        if not invitation:
            abort(404, message="Invalid invitation token")
        
        # Check if invitation is valid
        if not invitation.is_valid:
            if invitation.is_expired:
                abort(400, message="This invitation has expired")
            elif invitation.is_used:
                abort(400, message="This invitation has already been used")
            else:
                abort(400, message="This invitation is no longer valid")
        
        # Check if invited email matches current user
        if current_user.email != invitation.email:
            abort(403, message="This invitation was sent to a different email address")
        
        # Check if user is already a member
        existing_membership = GroupUserModel.query.filter_by(
            group_id=invitation.group_id, user_id=current_user_id
        ).first()
        if existing_membership:
            abort(400, message="You are already a member of this group")
        
        # Add user to group
        group_user = GroupUserModel(group_id=invitation.group_id, user_id=current_user_id)
        invitation.mark_as_used()
        
        db.session.add(group_user)
        
        try:
            db.session.commit()
            group = GroupModel.query.get(invitation.group_id)
            return {
                "message": f"Successfully joined group '{group.name}'",
                "group": {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "invite_code": group.invite_code
                }
            }, 200
            
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while joining the group")


@blp.route("/group/join-by-code")
class JoinGroupByCode(MethodView):
    
    @jwt_required()
    @blp.arguments(GroupJoinByCodeSchema)
    def post(self, join_data):
        """Join a group using invite code"""
        current_user_id = get_jwt_identity()
        invite_code = join_data["invite_code"].upper().strip()
        
        # Find group by invite code
        group = GroupModel.query.filter_by(invite_code=invite_code).first()
        if not group:
            abort(404, message="Invalid group code")
        
        # Check if group is public (private groups require email invitation)
        if not group.is_public:
            abort(403, message="This is a private group. You need an email invitation to join.")
        
        # Check if user is already a member
        existing_membership = GroupUserModel.query.filter_by(
            group_id=group.id, user_id=current_user_id
        ).first()
        if existing_membership:
            abort(400, message="You are already a member of this group")
        
        # Add user to group
        group_user = GroupUserModel(group_id=group.id, user_id=current_user_id)
        db.session.add(group_user)
        
        try:
            db.session.commit()
            return {
                "message": f"Successfully joined group '{group.name}'",
                "group": {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "invite_code": group.invite_code
                }
            }, 200
            
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while joining the group")


@blp.route("/group/code/<string:code>")
class GroupCodeInfo(MethodView):
    
    def get(self, code):
        """Get group information by invite code (public endpoint for previews)"""
        invite_code = code.upper().strip()
        
        group = GroupModel.query.filter_by(invite_code=invite_code).first()
        if not group:
            abort(404, message="Invalid group code")
        
        # Only show info for public groups
        if not group.is_public:
            abort(403, message="This is a private group")
        
        member_count = GroupUserModel.query.filter_by(group_id=group.id).count()
        
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "invite_code": group.invite_code,
            "member_count": member_count,
            "is_public": group.is_public
        }, 200


