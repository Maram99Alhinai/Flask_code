from bson import ObjectId
from flask import Blueprint, render_template,request,flash, redirect, url_for,jsonify,session, make_response, after_this_request
from flask_login import  login_required, current_user
from pymongo import MongoClient
from .form import *
import openpyxl
# from openpyxl.writer.excel import save_virtual_workbook
from io import BytesIO
import pandas as pd
import json
import urllib.parse


views = Blueprint('views', __name__)
atlas_connection_string = 'mongodb+srv://testflaskprojecttest:flasktest@cluster0.1u5lrml.mongodb.net/hasad'
# client = MongoClient('localhost', 27017)
client = MongoClient(atlas_connection_string)
db = client['hasad']
users_collection = db['users']
googleUsers_collection = db['googleUsers']
forms_collection = db['forms']
questions_collection = db['Questions']
Responders_collection = db['Responders']



@views.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response





@views.route('/')
def welcome():
    forms_created = forms_collection.count_documents({})

    users_count = users_collection.count_documents({})
    google_users_count = googleUsers_collection.count_documents({})

    #find top ueser name 
    total_users = users_count + google_users_count
    pipeline = [
        {"$group": {"_id": "$creator_email", "doc_count": {"$sum": 1}}},
        {"$sort": {"doc_count": -1}},
        {"$limit": 1}
    ]

    result = list(forms_collection.aggregate(pipeline))

    if result:
        most_documents_email = result[0]['_id']
    else:
        most_documents_email=' '

    # Query the "users" collection to find the user with the matching email
    user_document_in_users = users_collection.find_one({"email": most_documents_email})
    # Query the "googleUsers" collection to find the user with the matching email
    user_document_in_google_users = googleUsers_collection.find_one({"email": most_documents_email})

    if user_document_in_users:
        top_user = user_document_in_users.get("first_name")
    elif user_document_in_google_users:
        top_user = user_document_in_google_users.get("first_name")
    else:
        top_user="It can be you"
    user_email = get_user_email()
    # print(forms_created, total_users, top_user, user_email)
    return render_template("welcome.html", forms_created=forms_created, total_users=total_users, top_user=top_user,user_email=user_email)





@views.route('/my_forms', methods=['GET', 'POST'])
@login_required
def my_forms():
    
    text = f"Help us fill the form "
    user_email = get_user_email()
    user_name = get_user_name()
    published_forms,Draft_forms = divide_forms(user_email)
    if Draft_forms:
        draft_stat=True
    else:
        draft_stat=False
    
    
    # for emails post  
    if request.method == 'POST' :
        data = request.get_json()
        print(data)
        data['emails'] = [email.rstrip('x') for email in data['emails']]
        print(data['emails'])
        if data:
            send_form(data['formId'],*data['emails'])
            return redirect(url_for('views.my_forms'))
        else:
            return redirect(url_for('views.my_forms'))

    social_links = {
        'twitter': f'https://twitter.com/intent/tweet?text={text}',
        'facebook': f'https://www.facebook.com/sharer/sharer.php?',
        'instagram': 'https://www.instagram.com'
    }


    return render_template("my_forms.html", published_forms=published_forms, user_name=user_name,draft_stat=draft_stat, links=social_links)





@views.route('/my_forms/social', methods=['GET', 'POST'])
@login_required
def social_links():
    if request.method == 'POST' :
        scial_data = request.get_json()
        formTitle = scial_data['formTitle']
        shareLink = scial_data['shareLink']
        formId = scial_data['formId']
        text = f"Help us fill out the form titled '{formTitle}' by going to the link {shareLink} "
        
        encoded_url = urllib.parse.quote(shareLink, safe='')

        links = {
        'twitter': f'https://twitter.com/intent/tweet?text={text}',
        'facebook': f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}',
        'instagram': 'https://www.instagram.com'
        }
        
        return links
    
    
    


@views.route('/submit')
def submit():
    form_title = session.get('form_title', '')
    return render_template("submit.html", form_title=form_title)





@views.route('/my_darfts', methods=['GET', 'POST'])
@login_required
def my_darfts():
    user_name = get_user_name()
    user_email = get_user_email()
    _,Draft_forms = divide_forms(user_email)

    if request.method == 'POST':
        data = request.get_json()
        print(data)
        data['emails'] = [email.rstrip('x') for email in data['emails']]
        print(data['emails'])
        if data:
            send_form(data['formId'],*data['emails'])
            return redirect(url_for('views.my_forms'))
        else:
            return redirect(url_for('views.my_forms'))
    return render_template("my_darfts.html", Draft_forms=Draft_forms,user_name=user_name)





@views.route('/my_form3', methods=['GET', 'POST'])
@login_required
def my_form3():
    user_name = get_user_name()
    if request.method == 'POST':

        form_data = request.get_json()
        form_id=generate_form_id()

        # Insert the document into the forms collection
        new_form = make_form_doc(form_data,form_id) 
        forms_collection.insert_one(new_form)
   
        # Insert the document into the question collection
        new_questions=make_question_doc(form_data,form_id)
        questions_collection.insert_one(new_questions)
        
        # Insert the document into the question collection
        empty_respond_doc=make_empty_respond_doc(form_id)
        Responders_collection.insert_one(empty_respond_doc)
        
        return redirect(url_for('views.my_darfts'))
        

    return render_template("my_form3.html", user_name=user_name)






@views.route('/respo/<form_id>')
@login_required
def respo(form_id):
    user_name = get_user_name()
    user_email = session.get('email', None)  # Google
    if user_email is None:  # Non-Google
        user_email = session.get('_user_id', None)
    user_data = users_collection.find_one({'email': user_email})
    user_first_name = user_data.get('first_name', '') if user_data else ''

    form = forms_collection.find_one({"form_id": form_id})

    if form:
        form_creator_email = form.get("creator_email", "")
        form_title = form.get("form_title", "")
        form_description = form.get("description", "")

        if user_email == form_creator_email:  # Check if the user is the form creator
            form_id_to_find = form_id
            document = Responders_collection.find_one({"form_id": form_id_to_find})

            if document:
                object_id = document.get("_id")
                response_data = Responders_collection.find_one({"_id": object_id})

                if response_data:
                    respond_data = response_data.get("respond", {})
                    # Number of responded
                    total_responds = len(respond_data)
                    # Average time
                    total_time_seconds = 0
                    total_responses = len(respond_data)
                    for respond_key, respond_value in respond_data.items():
                        time_seconds = int(respond_value.get("time", 0))
                        total_time_seconds += time_seconds
                    if total_responses==0:
                        average_time_minutes="0"
                    else:
                        average_time_seconds = total_time_seconds / total_responses
                        average_time_minutes = round(average_time_seconds / 60)

                    # Find the most frequent device type
                    device_type_counts = {}
                    for respond_key, respond_value in respond_data.items():
                        device_type = respond_value.get("device")
                        if device_type:
                            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
                    if device_type_counts:
                        most_frequent_device = max(device_type_counts, key=device_type_counts.get)
                    else:
                        most_frequent_device="No Responds"
                    
                    #put responses in a dictionary
                    question_answers = {}
                    for respond_key, respond_value in respond_data.items():
                        answer_data = respond_value.get("answer", {})
                        for question_key, question_answer in answer_data.items():
                            if question_key in question_answers:
                                question_answers[question_key].append(question_answer)
                            else:
                                question_answers[question_key] = [question_answer]

                    question_info = {}
                    for respond_key, respond_value in respond_data.items():
                        answer_data = respond_value.get("answer", {})
    
                        for question_key in answer_data:
                            # Retrieve the question type and question text from the questions collection
                            question_document = questions_collection.find_one({"form_id": form_id_to_find})
                            if question_document:
                                questions_data = question_document.get("questions", {}).get("page_1", {})
                                if question_key in questions_data:
                                    question_info[questions_data[question_key]["question"]] = questions_data[question_key]["answer_type"]
                    
                    combined_dict = {}
                    for (question, question_type), (question_num, answers) in zip(question_info.items(), question_answers.items()):
                        combined_dict[question] = {"type": question_type, "answers": answers}

                    
                    


                    return render_template("dashboard.html", form_title=form_title, form_description=form_description,
                                           total_responds=total_responds, average_time_minutes=average_time_minutes,
                                           most_frequent_device=most_frequent_device,user_first_name=user_first_name,question_info=question_info, question_answers=question_answers,combined_dict=combined_dict,form_id=form_id,user_name=user_name)

        # If the user is not the form creator or the form does not exist, you can redirect or display an error message
        flash("You don't have permission to access this form.")
        return redirect(url_for('views.welcome'))  # Redirect to another page or route

    # If the form does not exist, you can display an error message or handle it as needed
    flash("The specified form does not exist.")
    return redirect(url_for('views.my_forms'))  # Redirect to another page or route





@views.route('/download_excel/<form_id>')
def download_excel(form_id):
    # Replace this with code to fetch data from your database
    response_data = Responders_collection.find_one({"form_id": form_id})
    questions = questions_collection.find_one({"form_id": form_id})
    if response_data and questions:
        questions_dict = questions['questions']
        questions_list = [question['question'] for page in questions_dict.values() for question in page.values()]
        if response_data['respond']:
            responses_dict = response_data['respond']
            question_key_map = {question: 'question_' + str(i+1) for i, question in enumerate(questions_list)}
            responses_list = [[answer[question_key_map[question]] for question in questions_list] for response in responses_dict.values() for answer in [response['answer']]]
            data = [questions_list] + responses_list
            print(data)
        else:
            data=[]
    # Create an Excel workbook and add data
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in data:
        ws.append(row)

    # Save the workbook to a BytesIO buffer
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Create a response with the Excel file
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=my_data.xlsx'

    return response





@views.route('/delete/<form_id>', methods=['POST'])
@login_required
def delete(form_id):
    forms_collection.delete_one({"form_id": form_id})
    Responders_collection.delete_one({"form_id": form_id})
    questions_collection.delete_one({"form_id": form_id})

    
    return jsonify({'result': 'success'}), 200





@views.route('/edit/<form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    user_name = get_user_name()
    if request.method == 'GET':
        
        form_doc = forms_collection.find_one({"form_id":form_id})
        if form_doc:
            formid = form_doc['form_id']
            questions_doc = questions_collection.find_one({"form_id": formid})
            if questions_doc:
                edit_mode = True
                form_doc.pop('_id', None)
                form_doc.pop('creation_date', None)
                questions_doc.pop('_id', None)
                form_json = json.dumps(form_doc)
                questions_json = json.dumps(questions_doc)
                
                return render_template("my_form3.html", user=current_user, form_json=form_json, questions_json=questions_json, edit_mode=edit_mode,form_id=form_id, user_name=user_name)
            else:
               flash('Form not found', 'error')
               return render_template("my_forms.html")
        else:
            flash('Form not found', 'error')
            return render_template("my_forms.html")

    if request.method == 'POST':
    
        form_data = request.get_json()
        print("form_data post",form_id)
        update_form_doc(form_data,form_id)
        replaced_Question_doc(form_data,form_id)

        return redirect(url_for('views.my_darfts'))

        # Redirect back to the form page
    return render_template("my_form3.html", user=current_user, form_json=form_json, questions_json=questions_json,
                            edit_mode=edit_mode,form_id=form_id, user_name=user_name)
    




@views.route('/share/<form_id>', methods=['GET', 'POST'])
def share(form_id):
    view_state=False
    form = forms_collection.find_one({"form_id": form_id})
    if form:
        form_title = form.get("form_title", "")
        form_description = form.get("description", "")
        question_document = questions_collection.find_one({"form_id": form_id})
        if question_document:
            questions = question_document.get("questions", {})
            result = []

            for page_num, page_data in questions.items():
                for question_key, question_info in page_data.items():
                    question_dict = {
                        "question": question_info.get("question", ""),
                        "answer_type": question_info.get("answer_type", ""),
                        "page_num": page_num,
                        "require": question_info.get("require", 0)
                    }
                    if "options" in question_info:
                        question_dict["options"] = question_info["options"]
                    result.append(question_dict)
            print(result)            
            page_details = {}
            for item in result:
                page_num = item['page_num']
                if page_num not in page_details:
                    page_details[page_num] = []
                question_info = {
                    'question': item['question'],
                    'require': item['require'],
                }
                if item['answer_type'] != 'simple_text':
                    question_info['options'] = item['options']
                page_details[page_num].append(question_info)
                print(page_details)
            if request.method == 'POST':
                form_data = request.form
                time_taken = form_data.get('time_taken')
                device_type = form_data.get('device_used')
                existing_document = Responders_collection.find_one({'form_id': form_id})
                if existing_document:
                    respond_counter = len(existing_document['respond']) + 1
                    answer_dict = {f'question_{i+1}': form_data[key] for i, key in enumerate(form_data) if key not in ['form_id', 'time_taken', 'device_used']}
                    new_respond = {
                        f'respond_{respond_counter}': {
                            'answer': answer_dict,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'time': time_taken, 
                            'device': device_type,
                        }
                    }
                    existing_document['respond'].update(new_respond)
                    Responders_collection.update_one({'form_id': form_id}, {'$set': {'respond': existing_document['respond']}})
                    update_respo_number(form_id)
                    return redirect(url_for('views.submit'))
            session['form_title'] = form_title
            return render_template("view.html",form_title=form_title,form_description=form_description,result=result,page_details=page_details,view_state=view_state)
        
    return redirect(url_for('views.welcome'))





@views.route('/publish/<form_id>', methods=['GET', 'POST'])
def publish(form_id):
  
    forms_collection.update_one(
        {"form_id": form_id},
        {"$set": {"published": 1}}
    )
    
    return redirect(url_for('views.my_forms'))





@views.route('/view/<form_id>', methods=['GET', 'POST'])
def view(form_id):
    view_state=True 
    user_name = get_user_name()
    form = forms_collection.find_one({"form_id": form_id})
    if form:
        form_title = form.get("form_title", "")
        form_description = form.get("description", "")
        publish_state = True if form.get("published", "") == 1 else False
        question_document = questions_collection.find_one({"form_id": form_id})
        if question_document:
            questions = question_document.get("questions", {})
            result = []

            for page_num, page_data in questions.items():
                for question_key, question_info in page_data.items():
                    question_dict = {
                        "question": question_info.get("question", ""),
                        "answer_type": question_info.get("answer_type", ""),
                        "page_num": page_num,
                        "require": question_info.get("require", 0)
                    }
                    if "options" in question_info:
                        question_dict["options"] = question_info["options"]
                    result.append(question_dict)
            print(result)            
            page_details = {}
            for item in result:
                page_num = item['page_num']
                if page_num not in page_details:
                    page_details[page_num] = []
                question_info = {
                    'question': item['question'],
                    'require': item['require'],
                }
                if item['answer_type'] != 'simple_text':
                    question_info['options'] = item['options']
                page_details[page_num].append(question_info)



                
            return render_template("view.html",form_title=form_title,form_description=form_description,result=result,
                                       page_details=page_details,user_name=user_name,form_id=form_id,
                                       view_state=view_state,publish_state=publish_state)
            
               
    return redirect(url_for('views.welcome'))