import os
from flask import Flask
from  flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Init SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['UPLOAD_FOLDER'] = 'uploads'

    db.init_app(app=app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    # Create DB tables
    with app.app_context():
        db.create_all()

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Auth routes
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Non-auth routes
    from .signature_requests import signature_requests as signature_requests_blueprint
    app.register_blueprint(signature_requests_blueprint)

    return app