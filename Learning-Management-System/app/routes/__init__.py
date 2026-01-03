from flask import Flask
from flask_mongoengine import MongoEngine # Changed
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

# Initialize Extensions
db = MongoEngine() # Changed
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.course import course_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    return app