import datetime, re
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from django import template
from ..models import Task, TaskUser

from datetime import date

register = template.Library()

#*********************************************************************************************************************#
#
# Create task_status templatetag to check status of the task
@register.simple_tag(name="task_status")
def task_status(task_due_date, task_completed):
    today = timezone.now()
    # 1: completed, 0: incompleted, -1: not completed, -2: not completed + overdue 
    status = 0
    if not task_completed:
        if task_due_date < today:
            status = -2 #  x + bone
        else:
            status = 0 # blank
    else:
        if task_due_date < today:
            status = -1 # cross
        else:
            status = 1 # tick
    return status 

#*********************************************************************************************************************#
#
# Create is_overdue templatetag to check whether the task  is overdue or not 
@register.simple_tag(name="is_overdue")
def is_overdue(task_due_date):
    today = datetime.now()
    if task_due_date < today:
        return True
    else:
        return False

#*********************************************************************************************************************#
#
# Create format templatetag to return the format date to string YYYY-MM-DD 
@register.simple_tag(name="date_format")
def date_format(date=None):  
    if isinstance(date, datetime):
        return datetime.strftime(date, "%Y-%m-%d")
    elif isinstance(date, str):
        pattern = re.compile("\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])*")
        if bool(re.search(pattern, date)):
            return date
        else:
            today = datetime.now()
            new_date = today + timedelta(days = 1)
            return datetime.strftime(new_date, "%Y-%m-%d")  
    else:
        today = datetime.now()
        new_date = today + timedelta(days = 1)
        return datetime.strftime(new_date, "%Y-%m-%d")

#*********************************************************************************************************************#
#
# Create tomorrow templatetag to return the tomorrow date 
@register.simple_tag(name="tomorrow")
def tomorrow():
    today = datetime.now()
    new_date = today + timedelta(days = 1)
    return datetime.strftime(new_date, "%Y-%m-%d")

#*********************************************************************************************************************#
#
# Creae yesterday templatetag to return the yesterday date 
@register.simple_tag(name="yesterday")
def yesterday():
    today = datetime.now()
    new_date = today - timedelta(days = 1)
    return datetime.strftime(new_date, "%Y-%m-%d")

#*********************************************************************************************************************#
#
# Creae yesterday templatetag to return the day before n day 
@register.simple_tag(name="day_before")
def day_before(value=5):
    today = datetime.now()
    new_date = today - timedelta(days = value)
    return datetime.strftime(new_date, "%Y-%m-%d")
#*********************************************************************************************************************#
#
# Creae day_after templatetag to return the day after n day 
@register.simple_tag(name="day_after")
def day_after(value=5):
    today = datetime.now()
    new_date = today + timedelta(days = value)
    return datetime.strftime(new_date, "%Y-%m-%d")

#*********************************************************************************************************************#
#
# Creae percentage templatetag to return percentage of two number 
@register.simple_tag(name="percentage")
def percentage(number1, number2):
    try:
        number1 / number2
        return f"{round((number1 / number2 * 100), 2):.2f}"
    except ZeroDivisionError:
        return 0
    
#*********************************************************************************************************************#
#
# Creae percentage_string templatetag to return percentage string for the reports of user/task overview 
@register.simple_tag(name="percentage_string")
def percentage_string(number1, number2):
    try:
        number1 / number2    
        percent = f"({round((number1/number2*100),2):.2f}%)" 
        number1_length = len(str(number1))
        percent_length =  len(f"{percent}")
        space = f"{'&nbsp;' * (10 - percent_length)}"
        percentage_str = f"{number1}{space}{percent}"
        return mark_safe(percentage_str)
    except ZeroDivisionError:
        return None