from flask import Flask
from .extensions import db, socketio
from flask_login import LoginManager
from app.auth import auth as auth_blueprint
from app.routes import main as main_blueprint
from app.testroute import test_bp
from .monitor import set_background_app, start_background_thread



def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    socketio.init_app(app)

    
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
    app.register_blueprint(test_bp, url_prefix='/test')

    with app.app_context():
        db.create_all()
    
    set_background_app(app)  # Set app context for background task
    start_background_thread() 
        

    return app
