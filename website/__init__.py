from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, json
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_principal import Principal,Permission, RoleNeed,UserNeed,identity_changed,identity_loaded,Identity,AnonymousIdentity
import os
from flask_caching import Cache

db = SQLAlchemy()
socketio = SocketIO()
cache = Cache()
admin_permission = Permission(RoleNeed('ADMIN'))
customer_permission = Permission(RoleNeed('CUSTOMER'))

def create_database():
    db.create_all()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "sadasdas" 
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'redis'  # Đặt CACHE_TYPE là 'redis'
    app.config['CACHE_REDIS_HOST'] = 'redis'  # Địa chỉ Redis server
    app.config['CACHE_REDIS_PORT'] = 6379  # Cổng mặc định của Redis
    app.config['CACHE_REDIS_DB'] = 0  # Redis database index (mặc định là 0)
    app.config['CACHE_REDIS_PASSWORD'] = ''  # Mật khẩu Redis nếu có, để trống nếu không có
    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return 'This page does not exist', 404
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'


    socketio.init_app(app)
    cache.init_app(app)
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

    from kafka import KafkaProducer
    from datetime import datetime

    producer = KafkaProducer(bootstrap_servers='kafka:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
 
    @app.after_request
    def after_request(response):
        user_data =
        {
            'ip_address': request.remote_addr,
            'url': request.path,
            'method': request.method,
            'status_code': response.status_code, 
            'timestamp': datetime.utcnow().isoformat() 
            
        }

        producer.send('user_activity', value=user_data)
        return response
    return app

