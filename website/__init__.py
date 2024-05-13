from flask import Flask
from flask_pymongo import PyMongo
from .models import *
from flask_login import LoginManager
from flask_mail import Message
from flask_mail import Mail
from flask_oauthlib.client import OAuth

def create_app():
    app = Flask(__name__,static_folder='static')
    app.config['SECRET_KEY'] = '*'
    app.config['MONGO_URI'] = '*'
    app.config['SESSION_TYPE'] = 'filesystem'
    mongo = PyMongo(app)

    with app.app_context():
        create_test_db_if_not_exists(mongo)
        create_user_collection(mongo)
        create_google_users_collection(mongo)
        create_form_collection(mongo)
        create_Questions_collection(mongo)
        create_Responders_collection(mongo)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User(id)

    mail = Mail(app)
    oauth = OAuth(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app