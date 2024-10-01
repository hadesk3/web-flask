from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_principal import Principal,Permission, RoleNeed,UserNeed,identity_changed,identity_loaded,Identity,AnonymousIdentity
import os
db = SQLAlchemy()
socketio = SocketIO()
admin_permission = Permission(RoleNeed('ADMIN'))
customer_permission = Permission(RoleNeed('CUSTOMER'))

def create_database():
    db.create_all()

 
    
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "sadasdas" 
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return 'This page does not exist', 404
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'


    socketio.init_app(app)
    from .views import views
    from .auth import auth
    from .admin import admin
    from .chat import chat
    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(auth,url_prefix = "/")
    app.register_blueprint(admin, url_prefix = "/")
    app.register_blueprint(chat, url_prefix = "/")
    import logging
    with app.app_context():
        create_database()
    from .models import Customer
    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id)) 
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        user = Customer.query.get(identity.id)
        if user:
            for role in user.roles:
                identity.provides.add(RoleNeed(role.name))
                logging.debug(f"Roles provided: {identity.provides}")
        else:
            logging.debug("User not found")

    return app

