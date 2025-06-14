from flask import Flask
from .extensions import db
from flask_login import LoginManager
from app.auth import auth as auth_blueprint
from app.routes import main as main_blueprint
from app import socket


def create_app(config_class='config.Config'):
    app = Flask(__name__)

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    from app.models import User
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    
    # Initialize socketio with app
    socket.socketio.init_app(app)

    # Start background thread after app starts
    with app.app_context():
        socket.start_background_thread()

    return app
