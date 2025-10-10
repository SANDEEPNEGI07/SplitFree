import uuid
from flask import current_app
from threading import Thread

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required

from blocklist import BLOCKLIST

from schemas import UserSchema, UserLoginSchema
from db import db

from models import UserModel
from tasks import send_user_registration_email

blp = Blueprint("User", __name__, description="Opeartion on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Register a new user with unique email."""
        # Check if email already exists (usernames can be duplicate)
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="Email already exists")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        try:
            current_app.logger.info(f"🚀 Starting email process for {user.email}")
            
            current_app.logger.info(f"📧 Using direct email sending for {user.email}")
            email_result = send_user_registration_email(user.email, user.username)
            current_app.logger.info(f"📧 Direct email result for {user.email}: {email_result}")
            
            if email_result.get("status") == "error":
                current_app.logger.error(f"❌ Email sending failed: {email_result.get('message')}")
            else:
                current_app.logger.info(f"✅ Email sent successfully to {user.email}")
                    
        except Exception as e:
            current_app.logger.error(f"💥 Failed to send welcome email to {user.email}: {str(e)}")
            import traceback
            current_app.logger.error(f"💥 Full traceback: {traceback.format_exc()}")

        return {"message":"User created successfully"}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Login with email and password to get access tokens."""
        email = user_data["email"]
        password = user_data["password"]
        
        user = UserModel.query.filter(UserModel.email == email).first()

        if user and pbkdf2_sha256.verify(password, user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}
        
        abort(401, message="Invalid credentials.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh access token using refresh token.
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"access_token":new_token}

@blp.route("/logout")
class UserLogout(MethodView):
   
   @jwt_required()
   def post(self):
        """Logout user and add token to blocklist."""
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message":"Successfully logged out."}

@blp.route("/user/<int:user_id>")
class User(MethodView):
    
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get user details by ID."""
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    def delete(self, user_id):
        """Delete user permanently. Cannot delete if user has financial obligations."""
        user = UserModel.query.get_or_404(user_id)
        
        constraints = []
        
        expenses_count = user.expenses_paid.count()
        if expenses_count > 0:
            constraints.append(f"has paid for {expenses_count} expense(s)")
        
        splits_count = len(user.splits)
        if splits_count > 0:
            constraints.append(f"has {splits_count} outstanding expense split(s)")
        
        groups_count = len(user.groups)
        if groups_count > 0:
            constraints.append(f"is a member of {groups_count} group(s)")
        
        if constraints:
            constraint_text = ", ".join(constraints)
            abort(400, message=f"Cannot delete user. User {constraint_text}. Please resolve these obligations first.")
        
        db.session.delete(user)
        db.session.commit()

        return {"message":"User deleted successfully."}, 200