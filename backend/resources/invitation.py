import uuid
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import (GroupInviteEmailSchema, GroupInvitationSchema, GroupJoinByCodeSchema, GroupCodeInfoSchema)
from db import db
from models import (GroupModel, GroupUserModel, UserModel, GroupInvitationModel)
from utils.permissions import check_group_membership, check_group_admin

blp = Blueprint("Invitation", __name__, description="Operations on group invitations")

@blp.route("/group/<int:group_id>/invite-email")
class GroupEmailInvite(MethodView):

    @jwt_required()
    @blp.arguments(GroupInviteEmailSchema)
    @blp.response(201, GroupInvitationSchema)
    def post(self, invitation_data, group_id):
        """Send email invitation to join group"""
        current_user_id = get_jwt_identity()

        # Check if user is admin of the group
        if not check_group_admin(group_id, current_user_id):
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

            # Queue invitation email
            try:
                if hasattr(current_app, 'queue') and current_app.queue:
                    job = current_app.queue.enqueue(
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
                    current_app.logger.info(f"Invitation email job queued: {job.id}")
                else:
                    current_app.logger.warning("Redis queue not available, skipping invitation email")
            except Exception as e:
                current_app.logger.error(f"Failed to queue invitation email: {str(e)}")

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
