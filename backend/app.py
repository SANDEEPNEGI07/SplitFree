import os
from dotenv import load_dotenv
import redis
from rq import Queue

from flask import Flask, request, jsonify
from flask_smorest import abort, Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

from db import db
from blocklist import BLOCKLIST

from resources.group import blp as GroupBlueprint
from resources.user import blp as UserBlueprint
from resources.expense import blp as ExpenseBlueprint
from resources.settlement import blp as SettlementBlueprint
from resources.history import blp as HistoryBlueprint


def create_app(db_url = None):
    app = Flask(__name__)
    load_dotenv()

    # Setup Redis Queue for background jobs (optional - for local dev with Redis)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            connection = redis.from_url(redis_url)
            connection.ping()  # Test connection
            app.queue = Queue(name="emails", connection=connection)
            app.logger.info("✅ Redis queue initialized for background jobs")
        except Exception as e:
            app.logger.warning(f"⚠️  Redis unavailable, emails will be sent synchronously: {e}")
            app.queue = None
    else:
        app.queue = None
        app.logger.info("ℹ️  No REDIS_URL set, emails will be sent synchronously")

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "SplitFree REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] ="3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["API_SPEC_OPTIONS"] = {
        "security": [{"BearerAuth": []}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Enable CORS for frontend communication
    allowed_origins = [
        os.getenv("FRONTEND_URL", "http://127.0.0.1:5000/swagger-ui"),
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://splitwise-api-frontend.onrender.com"
    ]
    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         supports_credentials=True,
         max_age=3600)

    api = Api(app)

    # Validate JWT secret key is configured
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")
    
    app.config["JWT_SECRET_KEY"] = jwt_secret
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return(
            jsonify(
                {"description":"The token has been revoked.","error":"token_revoked"}
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify(
                {
                    "description": "The token is not fresh",
                    "error": "fresh_token_required"
                }
            ),
            401
        )


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return(
            jsonify({"message": "The token has expired", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
            {
                "message":"Signature verification failed.", "error": "invalid_token"
            }
            ),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify(
                {
                    "description": "request does not contain an access token.",
                    "error": "authorization_required"
                }
            ),
            401
        )

    api.register_blueprint(GroupBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ExpenseBlueprint)
    api.register_blueprint(SettlementBlueprint)
    api.register_blueprint(HistoryBlueprint)

    return app

# Create app instance for Gunicorn
app = create_app()
