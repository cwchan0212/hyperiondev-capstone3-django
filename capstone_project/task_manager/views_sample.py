# Import the Django essential library timzone, render 
import requests, random

from .data import *
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render

# Import the django password library
from django.contrib.auth.hashers import make_password, check_password

# Import the django HttpResponse series library
from django.core import serializers
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import View, ListView
from .models import Task, TaskUser

# Create your views here.

#*********************************************************************************************************************#
# Login section

# Create index view to render the template home.html
def index(request):
    return render(request, "home.html")

# ---------------------------------------------------------------------------------------------------------------------#
# Create fetch view to render the template page by per click 
def fetch(request):    
    context = {}
    url = "https://type.fit/api/quotes"
    response = requests.get(url)
    quote = response.json()
    index = random.randint(0, len(quote))    
    author = quote[index]["author"] if quote[index]["author"] else ""
    content  = quote[index]["text"] if quote[index]["text"] else ""    
    context = {
        "Author": author,
        "Content": content,
    }    
    return render(request, "home.html", context)    
# ---------------------------------------------------------------------------------------------------------------------#
# Create a quote view to test the ajax under Django framework 
# Mixed Content: The page at '<URL>' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint '<URL>'. 
# This request has been blocked; the content must be served over HTTPS.
# Solution: http://bit.ly/3vUHaQn
# Method 1: Add this line <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"> inside <head> tag
# Method 2: By browser setting
# Firefox: 
# 1. type "about:config" 
# 2. find security.mixed_content.block_active_content. 
# 3. Set its value to false.
# Chrome:
# 1. Click Site Settings
# 2. Scroll down to Insecure content
# 3. Change it from Blocked (Default) to Allow
# 
def quote(request):    
    return render(request, "quote.html")

#---------------------------------------------------------------------------------------------------------------------#
# Create a login function to process the user login

# Route 1: User click the login button -> request method is POST + request.POST("submit")
# Route 1.1: request.POST.get("username") + request.POST.get("password") not blank -> retrieve the user's record -> render the template home.html
# Route 1.2: In any other case, render the template login.html
# Route 1.1.1: If the user's record is found -> Check whether the user's password match with our record
# Route 1.1.1.1: If the user's password is matched with our record -> render the template home.html
# Route 1.1.2: In any other case, render the template login.html
# Route 2: In any other case, render the template login.html

def login(request):
    context = {}
    if request.method == "POST" and request.POST.get("submit") == "login":
        # Check username and password 
        username = request.POST.get("username").strip()
        password = request.POST.get("password")
        if username and password:     
            user_queryset = TaskUser.get_user(TaskUser, username)
            # username found in the database
            if user_queryset:
                # if the passwords are matched                
                if check_password(password, user_queryset.user_password):
                    # Store the username, user_id and task_action into session
                    today = timezone.now()
                    user_updated_date = today.strftime("%Y-%m-%d %H:%M:%S")
                    user_row_affected = TaskUser.update_user(TaskUser, user_queryset.user_id, user_updated_date)     
                    request.session["user_username"] = username
                    request.session["user_id"] = user_queryset.user_id
                    request.session["view_type"] = "view_all"
                    # redirect to index page
                    message = f"Login successfully!"
                    # message = f"The task {task_id} is updated successfully."
                    context = Task.query_tasks(message, username)
                    return render(request, "home.html", context)   
                    # return HttpResponse("You're logged in.")
                # If the passwords are not match
                else:
                    return login_failed(request)
                    # return HttpResponse("2.3 Your username and password didn't match.")
            # If the username is not found in the database
            else:
                return login_failed(request)
        # Either username or password is empty
        else:
            return login_failed(request)
    else:
        return render(request, "login.html", context)

#---------------------------------------------------------------------------------------------------------------------#
# Create a logout function to clear the user's session and render the template login.html
def logout(request):
    try:
        del request.session["user_username"]
    except KeyError:
        pass
    return render(request, "home.html")

#---------------------------------------------------------------------------------------------------------------------#
# Create login_failed function to handle the case that the user fails to log in
def login_failed(request):
    message = f"Your username/password is not valid."
    context = {"Message": message}
    return render(request, "login.html", context)

def login_status(request):
    status = False
    if "user_id" in request.session:
        status = True
    return status

#*********************************************************************************************************************#
# User section
# Create a user_index view to handle the retrieval of the user's records and render the template user/index.html
def user_index(request):    
    if login_status == False: login(request)
    user_queryset = TaskUser.all_users(TaskUser, -1)
    context = {
        "User": user_queryset,
    }
    return render(request, "user/index.html", context)

#---------------------------------------------------------------------------------------------------------------------#
# Create a user_register function to handle the user registration

# Route 1: request.method == "POST" + request.POST.get("submit") == "register" -> check username and password
# Route 1.1: username is blank -> render the template user/form.html
# Route 1.2: username is not blank, check any existing username
# Route 1.2.1: If the username exists -> render the template user/form.html
# Route 1.2.2: If the username does not exist, check password1 and password2
# Route 1.2.2.1: If password1 and password2 are not matched -> render the template user/form.html
# Route 1.2.2.2: If password1 and password2 are matched -> register the new username, render the template user/form.html
# Route 2: In any other cases, render the template user/form.html

def user_register(request):
    context = {}
    message = ""
    code = -1 
    if request.method == "POST" and request.POST.get("submit") == "register":
        username = request.POST.get("username").strip()
        password1 = request.POST.get("password1") 
        password2 = request.POST.get("password2") 
        if not username:
            message = f"The username cannot be blank."
        else:
            user_queryset = TaskUser.get_user(TaskUser, username)
            if user_queryset:
                message = f"The username [{username}] exists."
            else:
                if password1 != password2:
                    message = f"The passwords are not matched."
                else:
                    user_id = TaskUser.new_id(TaskUser)
                    password1 = make_password(password1)
                    user_dictionary = {
                        "user_id": user_id,
                        "user_username": username,
                        "user_password": password1,
                    }
                    user_row_affected = TaskUser(**user_dictionary).save()
                    message = f"The user [{username}] is registered successfully." 
                    code = 1
        if message != "":
            context = {"Message": message, "Code": code}
            return render(request, "user/form.html", context)
    else:
        return render(request, "user/form.html")

#*********************************************************************************************************************#
# Task section
# Create a task_index view to load the tasks depending on the session of task_action
#
# Route 1: request.session["task_action"] exist -> check the value of request.session["task_action"] 
# Route 1.1: request.session["task_action"] == "view_mine" -> render the template task/index.html with the records of my tasks
# Route 1.2: request.session["task_action"] == "view_all" -> render the template task/index.html with the records of all tasks
# Route 2: request.session["task_action"] does not exist -> render the template task/index.html with the records of all tasks
def task_index(request):
    if login_status == False: login(request)    
    if "task_action" in request.session:
        if request.session["view_type"] == "view_mine":
            context = Task.view_task(request, 0)
            return render(request, "task/index.html", context)
        else:
            context = Task.view_task(request, 1)
            return render(request, "task/index.html", context)
    else:    
        context = {}
        task_queryset = Task.all_tasks(Task, -1)
        user_queryset = TaskUser.all_users(TaskUser)
        context = {
            "Task": task_queryset,
            "User": user_queryset,
        }
        return render(request, "task/index.html", context)

#---------------------------------------------------------------------------------------------------------------------#
# Create task_view function to handle the user's click: View All and View Mine
#
# Route 1: request.method == "POST" and request.POST.get("task_action") == "view_mine" and request.session["user_username"]
#          User clicks the button View Mine, query my tasks, store session user_action -> render the template task/index.html
# Route 2: request.method == "POST" and request.POST.get("task_action") == "view_all"
#          User clicks the button View All, query all tasks, store session user_action -> render the template task/index.html
# Route 3: request.method == "POST" and request.POST.get("task_action") == "add_task"
#          User clicks the button Add Task, query all users' records, render the template user/form.html
def task_view(request):
    if login_status == False: login(request)
    task_queryset, user_queryset = "", ""
    context = {}
    if request.method == "POST" and request.POST.get("view_type") == "view_mine" and "user_username" in request.session:
        context = Task.view_task(request, 0)
        request.session["view_type"] = "view_mine"
        return render(request, "task/index.html", context)
    elif request.method == "POST" and request.POST.get("view_type") == "view_all" and "user_username" in request.session:
        context = Task.view_task(request, 1, None)
        request.session["view_type"] = "view_all"
        return render(request, "task/index.html", context)
    elif request.method == "POST" and request.POST.get("task_action") == "add_task" and "user_username" in request.session:
        user_queryset = TaskUser.all_users(TaskUser)
        action = "add"
        context = {
            "Task": task_queryset,
            "User": user_queryset,
            "Action": action, 
        }   
        return render(request, "task/form.html", context)
    else:
        return HttpResponseRedirect("/task")

#---------------------------------------------------------------------------------------------------------------------#
# Create task_form view to handle the user to add task
# 
# Route 1: request.POST.get("task_action") == "add_task" and not request.POST.get("submit")
#           User clicks the button to add a task and submit, query all users record -> render the template task/form.html
# Route 2: request.POST.get("task_action") == "add_task" and request.method == "POST" and request.POST.get("submit") == "add_task_save"
#           User clicks the button to submit an added task, generate the new task_id, add a new task to the task record 
#           -> render the template task/form.html
# Route 3: request.POST.get("task_action") == "mark_complete" and request.method == "POST" and request.POST.get("task_id")
#           User clicks the button to mark the task complete, update the task record -> render the template task/index/html 
# Route 4: request.POST.get("task_action") == "edit_task" and not request.POST.get("submit") == "edit_task_save" and request.method == "POST" and request.POST.get("task_id")
#           User clicks the button to edit the task, query user and task record -> render the template task/form.html
# Route 5: request.POST.get("task_action") == "edit_task" and request.POST.get("submit") == "edit_task_save" and request.method == "POST" and request.POST.get("task_id")
#           User clicks the button to submit to saved task -> render the template task/index.html   
def task_form(request):
    context = {}
    # task_dictionary = {}
    # Create a new form for adding a new task
    if request.POST.get("task_action") == "add_task" and not request.POST.get("submit"):
        request.session["task_action"] = "add_task"
        user_queryset = TaskUser.all_users(TaskUser)
        context = {
            "User": user_queryset,
            "Action": "add_task",
        }
        
        return render(request, "task/form.html", context)
    # Save the new task
    elif request.POST.get("task_action") == "add_task" and request.method == "POST" and request.POST.get("submit") == "add_task_save":
        request.session["task_action"] = "add_task"
        task_user_id = request.POST.get("task_user_id").strip()
        task_fields = ['task_title', 'task_description', 'task_due_date', 'task_user_id']
        task_dictionary = {}
        is_error = False
        error_field_list = []
        if task_user_id:
            task_id = Task.new_id(Task)
            task_dictionary["task_id"] = task_id
            task_dictionary["task_completed"] = False
            for key, value in request.POST.items():
                if key in task_fields:
                    value = value.strip()
                    if value == "":
                        is_error = True 
                        error_field_list.append(key)

                    if key == "task_user_id":
                        task_dictionary["taskuser"] = TaskUser(value)
                    else:
                        task_dictionary[key] = value
            
            user_queryset = TaskUser.all_users(TaskUser)
            context["User"] = user_queryset
            if is_error:
                error_field_str = ", ".join([ error.replace('_', ' ').capitalize() for error in error_field_list])
                message = f"The field(s) [{error_field_str}] cannot be blank." 
                context = {
                    "Task": task_dictionary,
                    "Message": message,
                    "User": user_queryset,
                    "Action": "add_task",
                }
                return render(request, "task/form.html", context)
            else:
                task_row_affected = Task(**task_dictionary).save()
                task_title = task_dictionary["task_title"]
                message = f"The task [{task_title}] is added successfully."
                context = Task.query_tasks(message)
                context["Action"] = "add_task"
                context["User"] = user_queryset
                return render(request, "task/form.html", context)
    # Mark task complete
    elif request.POST.get("task_action") == "mark_complete" and request.method == "POST" and request.POST.get("task_id"):
        context["Action"] = "mark_complete"
        request.session["task_action"] = "mark_complete"
        task_id = request.POST.get("task_id")
        task_title = Task.get_task(Task, task_id)
        task_row_affected = Task.mark_complete(Task, task_id)
        message = f"The task [{task_title}] is marked as complete successfully."
        context = Task.view_task(request, 0, message)
        request.session["view_type"] = "view_mine"
        return render(request, "task/index.html", context)
    # Load the edit task form
    elif request.POST.get("task_action") == "edit_task" and not request.POST.get("submit") == "edit_task_save" and request.method == "POST" and request.POST.get("task_id"):
        request.session["task_action"] = "edit_task"
        task_id = request.POST.get("task_id")
        task_queryset = Task.edit_task(Task, task_id)
        user_queryset = TaskUser.all_users(TaskUser)
        action = "edit_task"
        context = { 
            "Task": task_queryset, 
            "User": user_queryset,
            "Action": action,
        }        
        return render(request, "task/form.html", context) 
    # Save the edited task
    elif request.POST.get("task_action") == "edit_task" and request.POST.get("submit") == "edit_task_save" and request.method == "POST" and request.POST.get("task_id"):
        context["Action"] = "edit_task"
        request.session["task_action"] = "edit_task"
        task_fields = ["task_title", "task_description", "task_due_date", "task_id"]
        task_id = request.POST.get("task_id")
        task_dictionary = {}
        is_error = False
        error_field_list = []
        for key, value in request.POST.items():
            if key in task_fields:
                value = value.strip()
                if value == "":
                    is_error = True 
                    error_field_list.append(key)
                if key != "task_user_id":
                     task_dictionary[key] = value
                     
        user_queryset = TaskUser.all_users(TaskUser)             
        context["User"] = user_queryset
        if is_error:
            error_field_str = ", ".join([ error.replace('_', ' ').capitalize() for error in error_field_list])
            message = f"The field(s) [{error_field_str}] cannot be blank" 
            context = {
                "Task": task_dictionary,
                "Message": message,
                "User": user_queryset,  
                "Action": "edit_task",
            }
            return render(request, "task/form.html", context)
        else:
            
            task_row_affected = Task.edit_task_save(Task, task_id, task_dictionary)
            task_title = task_dictionary["task_title"] 
            message = f"The task [{task_title}] is updated successfully."
            request.session["view_type"] = "view_mine"
            context = Task.view_task(request, 0, message)
            return render(request, "task/index.html", context)
        
    else:
        return HttpResponseRedirect("task")

#*********************************************************************************************************************#
# Report section 
#
# Create report_index view to load the reports of user and task overview
def report_index(request):
    if login_status == False: login(request)
    task_overview = Task.overview(Task)
    user_overview = TaskUser.overview(TaskUser)["data"]
    user_count = TaskUser.count(TaskUser, 0)
    task_count = Task.count(Task, 0)
    context = {
        "task_overview": task_overview,
        "user_overview": user_overview,
        "user_count": user_count,
        "task_count": task_count,        
    }

    return render(request, "report/index.html", context)

#---------------------------------------------------------------------------------------------------------------------#
# Create report_print function to load the preview report 
#
def report_print(request):
    if login_status == False: login(request)
    task_overview = Task.overview(Task)
    user_overview = TaskUser.overview(TaskUser)["data"]
    user_count = TaskUser.count(TaskUser, 0)
    task_count = Task.count(Task, 0)
    context = {
        "task_overview": task_overview,
        "user_overview": user_overview,
        "user_count": user_count,
        "task_count": task_count,        
    }
    return render(request, "report/print.html", context)

