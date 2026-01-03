from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask_mail import Mail

# =======================
# Extensions (GLOBAL)
# =======================
db = MongoEngine()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


# =======================
# Application Factory
# =======================
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # -----------------------
    # Register Blueprints
    # -----------------------
    from app.routes.auth import auth_bp
    from app.routes.course import course_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(course_bp, url_prefix="/courses")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(main_bp)

    # -----------------------
    # Home Route
    # -----------------------
    @app.route("/")
    def home():
        return "<h1>LMS Project is Running! 🚀</h1><a href='/auth/login'>Login</a>"

    return app
