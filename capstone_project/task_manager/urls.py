# Import Django Debug Toolbar library
from django.urls import path, include
from . import views

urlpatterns = [
#---------------------------------------------------------------------------------------------------------------------#
    # Map the path to the Django Debug Toolbar
    # path('__debug__/', include('debug_toolbar.urls')),
#---------------------------------------------------------------------------------------------------------------------#
    # Map the paths to main page index and login/logout + random quote
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('fetch', views.fetch, name='fetch'),
    path('quote', views.quote, name='quote'),
   
#---------------------------------------------------------------------------------------------------------------------#
    # Map the paths to the user index and registration
    path('user', views.user_index, name='user_index'),
    path('user/register', views.user_register, name='user_register'),
#---------------------------------------------------------------------------------------------------------------------#
    # Map the paths to the task index, task view and task action
    path('task', views.task_index, name='task_index'),
    path('task/view', views.task_view, name="task_view"),
    path('task/action', views.task_form, name='task_form'),
#---------------------------------------------------------------------------------------------------------------------#
    # Map the paths to the report index and report print 
    path('report', views.report_index, name='report_index'),
    path('report/print', views.report_print, name='report_print'),  

#---------------------------------------------------------------------------------------------------------------------#
    path('delete', views.delete_index, name='delete_index'),
    path('restore', views.restore_index, name='restore_index'),
    
]