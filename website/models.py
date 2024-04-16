from flask_pymongo import PyMongo
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


def create_test_db_if_not_exists(mongo):
    if 'TestDB' not in mongo.cx.list_database_names():
        mongo.cx['TestDB']

def create_user_collection(mongo):
    db = mongo.db
    if 'users' not in db.list_collection_names():
        db.create_collection('users')

def create_google_users_collection(mongo):
    db = mongo.db
    if 'googleUsers' not in db.list_collection_names():
        db.create_collection('googleUsers')

def create_form_collection(mongo):
    db = mongo.db
    if 'forms' not in db.list_collection_names():
        db.create_collection('forms')
        
def create_Questions_collection(mongo):
    db = mongo.db
    if 'Questions' not in db.list_collection_names():
        db.create_collection('Questions')
        
def create_Responders_collection(mongo):
    db = mongo.db
    if 'Responders' not in db.list_collection_names():
        db.create_collection('Responders')

class User(UserMixin):
    def __init__(self, id):
        self.id = id



