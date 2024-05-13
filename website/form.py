from flask import session,current_app
from datetime import datetime
import uuid
from bson import ObjectId
from pymongo import MongoClient
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message


atlas_connection_string = '*'
client = MongoClient(atlas_connection_string)
db = client['hasad']
users_collection = db['users']
googleUsers_collection = db['googleUsers']
forms_collection = db['forms']
questions_collection = db['Questions']
Responders_collection = db['Responders']
SECRET_KEY = '*'
mail = Mail()
serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_user_email():
    user_email = session.get('email', None) #google
    if user_email == None: #non google
        user_email=session.get('_user_id', None)
    return user_email

# Generate a custom form ID
def generate_form_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4()).replace('-', '')[:8]  # Generate a random 8-character identifier
    form_id = f'{timestamp}-{unique_id}'
    return form_id

def make_form_doc(data,form_id):

    #get data
    user_email=get_user_email()
    form_title = data['title']
    form_description = data['description']
    creation_date = datetime.now()
    
    # Create a new document for the forms collection

    new_form = {
        "_id":ObjectId(),
        "form_id": form_id ,
        "creator_email": user_email,
        "form_title": form_title,
        "description": form_description,
        "creation_date": creation_date,
        "published": 0,  # You can set this value as needed
        "respo_num": 0,  # Initialize response count
        "Share_link": f"https://hasad.smart-developer.net/share/{form_id}"
    }
    
    return(new_form)


def make_question_doc(data,form_id):
    # Initialize an empty dictionary for the transformed data
    qestion_doc = {
        "_id":ObjectId(),
        "form_id": form_id ,
        "questions": {}
    }    
    previous_page_number =1
    current_page_number = 1
    qestion_doc["questions"][f"page_{current_page_number}"] = {}
    for key, value in data.items():
        if key.startswith('question_') :
            question_number = int(key.split('_')[1])
            current_page_number=(question_number//10)+1
            previous_page_number +=1
            if current_page_number>previous_page_number:
                qestion_doc["questions"][f"page_{current_page_number}"] = {} 
            qestion_doc["questions"][f"page_{current_page_number}"][f"question_{question_number}"] = {
                "question": value,
                "answer_type": data[f'ans_type_{question_number}'],
                "require": int(data[f'require_{question_number}'])
            }
        elif key.startswith('option_'):
            option_number = key.split('_')[2]
            question_number = key.split('_')[1]
            if "options" not in qestion_doc["questions"][f"page_{current_page_number}"][f"question_{question_number}"]:
                qestion_doc["questions"][f"page_{current_page_number}"][f"question_{question_number}"]["options"] = []
            qestion_doc["questions"][f"page_{current_page_number}"][f"question_{question_number}"]["options"].append(value)
 
    
    return(qestion_doc)

def make_empty_respond_doc(form_id):
    
    # Initialize an empty dictionary for the respond data
    res_doc = {
        "_id":ObjectId(),
        "form_id": form_id ,
        "respond": {}
    }    
    
    return(res_doc)


def divide_forms(user_email):
    forms = forms_collection.find({'creator_email': user_email})
    published_forms = []
    Draft_forms = []

    for form in forms:
        if form.get('published') == 1:
            published_forms.append(form)
        elif form.get('published') == 0:
            Draft_forms.append(form)
    return(published_forms,Draft_forms)

def get_user_name():
    user_email=get_user_email()
    # Query the "users" collection to find the user with the matching email
    user_document_in_users = users_collection.find_one({"email": user_email})
    # Query the "googleUsers" collection to find the user with the matching email
    user_document_in_google_users = googleUsers_collection.find_one({"email": user_email})

    if user_document_in_users:
        user = user_document_in_users.get("first_name")
    elif user_document_in_google_users:
        user = user_document_in_google_users.get("first_name")
    else:
        user="unknown"
    return user


def get_user_type():
    user_email = session.get('email', None) #google
    if user_email != None: 
        user_type="google"
    else:
        user_type="non google"
    return user_type


def send_form(id,*emails):
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

            # Send an email with the reset link
    form_link ='https://hasad.smart-developer.net/share/' + str(id)
    subject = 'Form to Solve'
    message = f'Click the following link to solve the form: {form_link}'
    msg = Message(subject=subject,
                  recipients=list(emails),
                  html=message,
                  sender='hasad@smart-developer.net')
    mail.send(msg)
    
    
def update_form_doc(updated_data,form_id):
        
    #for form doc
    new_form = make_form_doc(updated_data,form_id)
    keys_to_remove = ["_id", "creator_email", "Share_link", "creation_date"]

    for key in keys_to_remove:
        new_form.pop(key, None)
    

    filter_criteria = {"form_id": form_id}  
    update_operation = {"$set": new_form}
    
    result1 = forms_collection.update_one(filter_criteria, update_operation)

    if result1.modified_count > 0:
        print("Document update_form_doc successfully")
    else:
        print("No documents matched the filter criteria")

    return result1



def replaced_Question_doc(updated_data,form_id):
    
    #for form doc
    new_ques_doc = make_question_doc(updated_data,form_id)
    new_ques_doc.pop('_id', None)

    filter_criteria = {"form_id": form_id}  
    
    result2 = questions_collection.replace_one(filter_criteria, new_ques_doc)

    if result2.modified_count > 0:
        print("Document replaced_Question_doc successfully")
    else:
        print("No documents matched the filter criteria")

    return result2



def update_respo_number(form_id):
    document = forms_collection.find_one({"form_id": form_id})
    forms_collection.update_one({'_id': document['_id']}, {'$set': {'respo_num': document["respo_num"]+1}})