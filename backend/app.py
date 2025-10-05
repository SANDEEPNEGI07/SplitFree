import os
from dotenv import load_dotenv
import redis
from rq import Queue, Worker
from threading import Thread

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

# Global variable to track worker thread status
worker_thread_started = False


def create_app(db_url = None):
    app = Flask(__name__)
    load_dotenv()

    # Setup Redis Queue for background jobs
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            connection = redis.from_url(redis_url)
            connection.ping()
            app.queue = Queue(name="emails", connection=connection)
            app.redis_connection = connection
        except Exception as e:
            app.queue = None
            app.redis_connection = None
    else:
        app.queue = None
        app.redis_connection = None
    
    # In-app RQ worker function - doesn't need a separate Bg worker
    def run_worker():
        """Background worker that runs in the same process"""
        try:
            worker = Worker(['emails'], connection=app.redis_connection)
            worker.work(with_scheduler=True)
        except Exception as e:
            if hasattr(app, 'logger'):
                app.logger.error(f"RQ worker failed: {e}")
    
    @app.before_request
    def start_worker_thread():
        global worker_thread_started
        if not worker_thread_started and hasattr(app, 'redis_connection') and app.redis_connection:
            try:
                worker_thread = Thread(target=app.run_worker, daemon=True)
                worker_thread.start()
                worker_thread_started = True
                app.logger.info("✅ Background worker thread started successfully")
            except Exception as e:
                app.logger.error(f"Failed to start background worker: {e}")
        
        # Remove this function after first execution to avoid repeated checks
        if worker_thread_started or not (hasattr(app, 'redis_connection') and app.redis_connection):
            app.before_request_funcs[None].remove(start_worker_thread)

    
    # Store worker function for later use
    app.run_worker = run_worker

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

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint with worker and Redis status"""
        status = {
            "status": "healthy",
            "redis_available": bool(app.redis_connection),
            "queue_available": bool(app.queue),
            "email_mode": "async" if app.queue else "sync"
        }
        
        # Test Redis connection if available
        if app.redis_connection:
            try:
                app.redis_connection.ping()
                status["redis_status"] = "connected"
            except:
                status["redis_status"] = "disconnected"
                status["redis_available"] = False
        else:
            status["redis_status"] = "not_configured"
            
        return jsonify(status)

   
    api.register_blueprint(GroupBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ExpenseBlueprint)
    api.register_blueprint(SettlementBlueprint)
    api.register_blueprint(HistoryBlueprint)

    return app

# Create app instance for Gunicorn
app = create_app()
