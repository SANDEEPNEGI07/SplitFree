import uuid
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256


from schemas import UserSchema
from db import db

from models import UserModel

blp = Blueprint("User", __name__, description="Opeartion on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Register user"""
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message = f"User already exists")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return {"message":"User created successfully"}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get user details"""
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        """Delete the user"""
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message":"User deleted."}, 200