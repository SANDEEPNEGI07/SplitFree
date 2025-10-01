import os
from dotenv import load_dotenv
import redis
from threading import Thread
from queue import Queue

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

    # Email Queue Setup (Redis optional, threading fallback)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            redis_conn = redis.from_url(redis_url)
            redis_conn.ping()
            app.redis = redis_conn
        except Exception as e:
            app.redis = None
    else:
        app.redis = None
    
    # Simple in-memory queue for email processing
    app.email_queue = Queue()
    app.email_thread_running = False

    def process_email_queue():
        """Process emails from the queue in background thread."""
        while True:
            try:
                email_task = app.email_queue.get(timeout=1)
                if email_task is None:  # Shutdown signal
                    break
                    
                func, args, kwargs = email_task
                func(*args, **kwargs)
                app.email_queue.task_done()
                
            except Exception as queue_error:
                # Log queue processing errors but continue running
                if hasattr(app, 'logger'):
                    app.logger.error(f"Email queue processing error: {queue_error}")
                continue
    
    app.process_email_queue = process_email_queue
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Enable CORS for frontend communication
    allowed_origins = [
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
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
