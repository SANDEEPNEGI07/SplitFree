import uuid
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import GroupSchema, UserIdSchema

from db import db

from models import GroupModel, GroupUserModel, UserModel

blp = Blueprint("Group", __name__, description="Operations on group")

@blp.route("/group")
class GroupList(MethodView):
    @blp.response(200, GroupSchema(many=True))
    def get(self):
        return GroupModel.query.all()

    @blp.arguments(GroupSchema)
    @blp.response(201, GroupSchema)
    def post(self, group_data):
        group = GroupModel(**group_data)
        try:
            db.session.add(group)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A group with that name already exists.")

        except SQLAlchemyError:
            abort(500, messgae="An error occured while creating group.")
        
        return group

    
@blp.route("/group/<int:group_id>")
class Group(MethodView):

    @blp.response(200, GroupSchema)
    def get(self, group_id):
        try:
            return GroupModel.query.get_or_404(group_id)
        except KeyError:
            abort(404, message="group not found.")

    def delete(self, group_id):
        group = GroupModel.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()

        return {"message":"Group deleted"}
    

@blp.route("/group/<int:group_id>/user")
class UserToGroup(MethodView):

    @blp.arguments(UserIdSchema)
    def post(self, user_data, group_id):
        user_id = user_data.get("user_id")
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

        return {"message":f"{UserModel.query.get(user_id).username} is added to {GroupModel.query.get(group_id).name}"}

@blp.route("/group/<int:group_id>/user/<int:user_id>")
class RemoveUserFromGroup(MethodView):
    def delete(self, group_id, user_id):
        group_user = GroupUserModel.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not group_user:
            abort(404, message="User not found in group")
        db.session.delete(group_user)
        db.session.commit()
        return {"message": "User removed from group"}, 200


