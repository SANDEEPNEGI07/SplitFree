import uuid
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required

from blocklist import BLOCKLIST

from sqlalchemy import or_


from schemas import UserSchema
from db import db

from models import UserModel

blp = Blueprint("User", __name__, description="Opeartion on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """
        Register a new user in the system.
        
        Creates a new user account with a hashed password. Username must be unique.
        Returns success message on successful registration.
        
        Args:
            user_data: JSON containing username and password
            
        Returns:
            201: Success message with user created confirmation
            409: Error if username already exists
        """
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message = f"User already exists")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return {"message":"User created successfully"}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """
        Authenticate user and provide access tokens.
        
        Validates user credentials and returns JWT access and refresh tokens
        for authenticated API access. Access token is marked as fresh.
        
        Args:
            user_data: JSON containing username and password
            
        Returns:
            200: Access token and refresh token on successful login
            401: Error if credentials are invalid
        """
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
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
        
        Generates a new access token using a valid refresh token. 
        The old refresh token is added to blocklist for security.
        New access token is marked as non-fresh.
        
        Requires:
            Valid refresh token in Authorization header
            
        Returns:
            200: New access token
            401: Error if refresh token is invalid or expired
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
        """
        Logout user and invalidate access token.
        
        Adds the current access token to the blocklist to prevent further use.
        User will need to login again to get new tokens.
        
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming logout
            401: Error if token is invalid or missing
        """
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message":"Successfully logged out."}

@blp.route("/user/<int:user_id>")
class User(MethodView):
    
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """
        Get user details by ID.
        
        Retrieves user information including ID and username.
        Password is never returned for security.
        
        Args:
            user_id: Unique identifier of the user
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: User object with id and username
            404: Error if user not found
            401: Error if token is invalid
        """
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    def delete(self, user_id):
        """
        Delete user account permanently.
        
        Removes user from the system including all associated data.
        This action cannot be undone.
        
        Args:
            user_id: Unique identifier of the user to delete
            
        Requires:
            Valid access token in Authorization header
            
        Returns:
            200: Success message confirming deletion
            404: Error if user not found
            401: Error if token is invalid
        """
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message":"User deleted."}, 200