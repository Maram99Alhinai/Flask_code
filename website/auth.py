from flask import Blueprint, abort, render_template, request, flash, current_app, session, redirect, url_for, after_this_request
from pymongo.errors import DuplicateKeyError 
from flask_pymongo import PyMongo
from pymongo import MongoClient
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from datetime import datetime, timedelta
import secrets
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_oauthlib.client import OAuth
from authlib.common.security import generate_token
import os
from google_auth_oauthlib.flow import Flow
import pathlib
import google.auth.transport.requests
from pip._vendor import cachecontrol
from google.oauth2 import id_token
import re 
from .form import get_user_type, get_user_email


auth = Blueprint('auth', __name__)
atlas_connection_string = '*'
client = MongoClient(atlas_connection_string)
db = client['hasad']
users_collection = db['users']
googleUsers_collection = db['googleUsers']
forms_collection = db['forms']
SECRET_KEY = 'hjshjhdjah kjshkjdhjs'
oauth = OAuth()
mail = Mail()
serializer = URLSafeTimedSerializer(SECRET_KEY)


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "*"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://hasad.smart-developer.net/callback"
)


def is_valid_password(password):
    # Your password validation logic
    if len(password) < 7 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password) or not any(char.isalnum() for char in password):
        return False
    return True

@auth.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@auth.route("/login_google")
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500) 

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["email"] = id_info.get("email")
    session["name"] = id_info.get("name")
    user = User(session["email"])
    existing_user = googleUsers_collection.find_one({'email': session["email"]})
    if existing_user:
        pass
    else:
        user_data = {
                'email': session["email"],
                'first_name': session["name"] 
            }
        googleUsers_collection.insert_one(user_data)
    login_user(user)
    return redirect(url_for('views.my_forms'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password1'], password):
            user = User(email)
            login_user(user)
            return redirect(url_for('views.my_forms'))

        else:
            flash('Login failed. Check your email and password.', category='error')
            session['submitted_data'] = {
                'email': email
            }
            return redirect(url_for('auth.login'))

    submitted_data = session.pop('submitted_data', {})
    return render_template("login.html",user=current_user,submitted_data=submitted_data)


@auth.route('/logout')
@login_required
def logout():
   session.clear()
   logout_user()
   return redirect(url_for('auth.login', _external=True))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        existing_user = users_collection.find_one({'email': email})

        if existing_user:
            flash('User with this email already exists. Please use a different email.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        elif first_name is None:
            flash('First name is required.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        elif not is_valid_password(password1):
            flash('Password must be at least 7 characters and contain at least one number, one character, and one symbol.', category='error')
            session['submitted_data'] = {
                'email': email,
                'firstName': first_name
            }
            return redirect(url_for('auth.sign_up'))
        else:
            hashed_password = generate_password_hash(password1, method='sha256')
            user_data = {
                'email': email,
                'first_name': first_name,
                'password1': hashed_password
            }
            try:
                users_collection.insert_one(user_data)
                user = User(email)
                login_user(user)

                flash('User registered successfully!', category='success')
                return redirect(url_for('views.my_forms'))

            except DuplicateKeyError:
                flash('User with this email already exists. Please use a different email.', category='error')


    submitted_data = session.pop('submitted_data', {})
    return render_template("sign_up.html",user=current_user, submitted_data=submitted_data)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = users_collection.find_one({'email': email})

        if user:
            # Generate a password reset token
            EMAIL="*"
            PASSWORD="*"
            
            current_app.config['MAIL_SERVER'] = '*'
            current_app.config['MAIL_PORT'] = 465
            current_app.config['MAIL_USE_SSL'] = True
            current_app.config['MAIL_USE_TLS'] = False
            current_app.config['MAIL_USERNAME'] = EMAIL
            current_app.config['MAIL_PASSWORD'] = PASSWORD
            mail = Mail()
            mail.init_app(current_app)
            token = serializer.dumps(email, salt='password-reset')

            # Send an email with the reset link
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            subject = 'Password Reset Request From Hasad'
            message = f'Click the following link to reset your password: {reset_link}'
            send_password_reset_email(email, subject, message,EMAIL)

            flash('Password reset instructions sent to your email.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found. Check your email address.', category='error')
            return redirect(url_for('auth.forgot_password'))

    return render_template("forgot_password.html", user=current_user)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600) #1 hour
    except Exception:
        flash('Invalid or expired token. Please request a new password reset.', category='error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash('Passwords do not match.', category='error')
        elif not is_valid_password(password1):
            flash('Password must be at least 7 characters.', category='error')
        else:
            hashed_password = generate_password_hash(password1, method='sha256')
            users_collection.update_one({'email': email}, {'$set': {'password1': hashed_password}})
            flash('Password reset successfully. You can now log in with your new password.', category='success')
            return redirect(url_for('auth.login'))
    return render_template("reset_password.html", user=current_user)

def send_password_reset_email(email, subject, message,sender):
    msg = Message(subject=subject,
                  recipients=[email],
                  html=message,
                  sender=sender)
    mail.send(msg)


@auth.route('/my_profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    user_email = session.get('email', None)
    if user_email == None: #non google
        user_email=session.get('_user_id', None)
        query = {"creator_email": user_email}
        count = forms_collection.count_documents(query)
        user_data = users_collection.find_one({'email': user_email})
        user_first_name = user_data.get('first_name', '') if user_data else ''
        user_last_name = user_data.get('last_name', '') if user_data else ''
        user_username = user_data.get('username', '') if user_data else ''
        user_gender = user_data.get('gender', '') if user_data else ''
        user_age = user_data.get('age', '') if user_data else ''
        
        if request.method == 'POST':
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            username = request.form.get('username')
            gender = request.form.get('gender')
            age = request.form.get('age')
        
            users_collection.update_one(
                    {'email': user_email},
                    {
                        '$set': {
                            'first_name': first_name,
                            'last_name': last_name,
                            'username': username,
                            'gender': gender,
                            'age': age
                        }
                    }
                )

            user_first_name = first_name
            user_last_name = last_name
            user_username = username
            user_gender = gender
            user_age = age
    else:
        query = {"creator_email": user_email}
        count = forms_collection.count_documents(query)
        user_data = googleUsers_collection.find_one({'email': user_email})
        user_first_name = user_data.get('first_name', '') if user_data else ''
        user_last_name = user_data.get('last_name', '') if user_data else ''
        user_username = user_data.get('username', '') if user_data else ''
        user_gender = user_data.get('gender', '') if user_data else ''
        user_age = user_data.get('age', '') if user_data else ''
        if request.method == 'POST':
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            username = request.form.get('username')
            gender = request.form.get('gender')
            age = request.form.get('age')
        
            googleUsers_collection.update_one(
                    {'email': user_email},
                    {
                        '$set': {
                            'first_name': first_name,
                            'last_name': last_name,
                            'username': username,
                            'gender': gender,
                            'age': age
                        }
                    }
                )

            user_first_name = first_name
            user_last_name = last_name
            user_username = username
            user_gender = gender
            user_age = age
    return render_template(
        "my_profile.html",
        user_email=user_email,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        user_username=user_username,
        user_gender=user_gender,
        user_age=user_age,
        count=count
    )