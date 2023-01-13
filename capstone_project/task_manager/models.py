from django.db import models
from django.utils import timezone
# Create your models here.
#======================================================================================================================#
# Define the Model Class "TaskUser" with its attributes

class TaskUser(models.Model):
    user_id = models.IntegerField(null = False, primary_key = True)
    user_username = models.CharField(null = False, max_length = 10)
    user_password = models.CharField(null = False, max_length = 100)
    user_created_date = models.DateTimeField(null = False, default = timezone.now )
    user_updated_date = models.DateTimeField(null = False, auto_now=True )
    user_deleted = models.BooleanField(default = False)    

#---------------------------------------------------------------------------------------------------------------------#
    # Create str representation to return its username
    def __str__(self):
        return f"{self.user_username}"
    
#---------------------------------------------------------------------------------------------------------------------#
    # Create new id of the user 
    def new_id(self):
        return TaskUser.objects.all().order_by("-user_id")[0].user_id + 1

#---------------------------------------------------------------------------------------------------------------------#
    # Create login function to get the records of all users
    def all_users(self, order=1):
        if order == 1:
            return self.objects.filter(user_deleted = False).order_by('user_id').values()
        else:
            return self.objects.filter(user_deleted = False).order_by('-user_id').values()
        
#---------------------------------------------------------------------------------------------------------------------#
    def get_user_id(self, user_username):
        try:
            user_id = self.object.filter(user_username = user_username).only("user_id")
        except:
            user_id = None
        return user_id
#---------------------------------------------------------------------------------------------------------------------#
    # Create update_user to update the user's info
    def update_user(self, user_id, user_updated_date):
        return self.objects.filter(user_id = user_id).update(user_updated_date = user_updated_date)
        
#---------------------------------------------------------------------------------------------------------------------#
    # Create a get_user function to get the records of the user by username
    def get_user(self, user_username):
        try: 
            user_queryset = TaskUser.objects.get(user_username = user_username) 
        except:
            user_queryset = None
        return user_queryset
#---------------------------------------------------------------------------------------------------------------------#
    # Create count function to return the number of users
    def count(self, type=1):
        # 1: all users, 0: not deleted. -1: deleted
        if type == -1:
            count = self.objects.filter(user_deleted = True).count()
        elif type == 0:
            count = self.objects.filter(user_deleted = False).count()
        else:
            count = self.objects.all().count()
        return count

#---------------------------------------------------------------------------------------------------------------------#
    # Create an overview function to collect the statistics of users
    def overview(self):
        # Sammple Report
        #
        # The total number of users registered with task_manager.py
        # The total number of tasks that have been generated and tracked using task_manager.py
        #                                     No. of tasks            No. of tasks          No. of ongoing      No. of uncompleted
        #                                     assigned (%)           completed (%)               tasks (%)        overdue task (%)
        # ------------------------------------------------------------------------------------------------------------------------
        # admin                                   2 ( 10%)                0 (  0%)                0 (  0%)                2 ( 10%)
        # boss                                    2 ( 10%)                0 (  0%)                2 ( 10%)                0 (  0%)
        # chris                                   4 ( 20%)                1 (  5%)                2 ( 10%)                1 (  5%)
        # john                                    4 ( 20%)                2 ( 10%)                2 ( 10%)                0 (  0%)
        # kay                                     3 ( 15%)                3 ( 15%)                0 (  0%)                0 (  0%)
        # mark                                    5 ( 25%)                2 ( 10%)                3 ( 15%)                0 (  0%)
        # ------------------------------------------------------------------------------------------------------------------------
        # total                                  20 (100%)                8 ( 40%)                9 ( 45%)                3 ( 15%)

        task_queryset =  Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False)
        user_queryset = self.objects.filter(user_deleted = False)
        user_list = []
        user_dictionary = {}
        assigned_sum, completed_sum, uncompleted_sum, uncompleted_and_overdue_sum = 0, 0, 0, 0

        for user in user_queryset:
            number_of_task_assigned = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False, taskuser_id = user.user_id).count()
            number_of_task_completed = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False, taskuser_id = user.user_id, task_completed = True).count()
            number_of_task_uncompleted = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False, taskuser_id = user.user_id, task_completed = False, task_due_date__lte=timezone.now()).count()
            number_of_task_uncompleted_overdue = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False, taskuser_id = user.user_id, task_completed = False, task_due_date__gte=timezone.now()).count()
            
            assigned_sum += number_of_task_assigned
            completed_sum += number_of_task_completed
            uncompleted_sum += number_of_task_uncompleted
            uncompleted_and_overdue_sum += number_of_task_uncompleted_overdue

            user_dictionary = {
                "id": user.user_id,
                "username": user.user_username,
                "assigned": number_of_task_assigned,
                "completed": number_of_task_completed,
                "uncompleted": number_of_task_uncompleted,
                "uncompleted_and_overdue": number_of_task_uncompleted_overdue,
            }
            user_list.append(user_dictionary)
        user_list.append({
                "id": 0,
                "username": "total",
                "assigned": assigned_sum,
                "completed": completed_sum,
                "uncompleted": uncompleted_sum,
                "uncompleted_and_overdue": uncompleted_and_overdue_sum,
            })

        user_dictionary = {
            "data": user_list
        }

        return user_dictionary


#======================================================================================================================#
# Define Task class with attributes
class Task(models.Model):
    task_id = models.IntegerField(null = False, primary_key = True)
    task_title = models.CharField(null = False, max_length = 50)
    task_description = models.CharField(null = False, max_length = 100)
    task_assign_date = models.DateTimeField(null = False, default = timezone.now )
    task_due_date = models.DateTimeField(null = False)
    task_completed = models.BooleanField(default = False)
    task_deleted = models.BooleanField(default = False)
    taskuser = models.ForeignKey(TaskUser, on_delete = models.CASCADE)

#---------------------------------------------------------------------------------------------------------------------#
    # Create str representation to return its task title
    def __str__(self):
        return f"{self.task_title}"

#---------------------------------------------------------------------------------------------------------------------#
    # Create a new id of the task 
    def new_id(self):
        return Task.objects.all().order_by("-task_id")[0].task_id + 1
    
#---------------------------------------------------------------------------------------------------------------------#
    # Create an all_tasks function to get the records of all tasks
    def all_tasks(self, order=1):
        if order == 1:
            return self.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False).order_by('task_id')
        else:
            return self.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False).order_by('-task_id')
#---------------------------------------------------------------------------------------------------------------------#
    def get_task(self, task_id):
        task_queryset = self.objects.get(task_id = task_id)
        return task_queryset
        
#---------------------------------------------------------------------------------------------------------------------#
    # Create mark_complete function to set task_completed as True
    def mark_complete(self, task_id):
        return self.objects.filter(task_id = task_id).update(task_completed = True)
    
#---------------------------------------------------------------------------------------------------------------------#
    # Create edit_task function to query the record of edit task 
    def edit_task(self, task_id):
        return self.objects.get(task_id = task_id)
    
#---------------------------------------------------------------------------------------------------------------------#
    # Create edit_task_save function to save the record of edit task 
    def edit_task_save(self, task_id, task_dictionary):
        task_row_affected = self.objects.filter(task_id = task_id).update(**task_dictionary)
        return task_row_affected
    
#---------------------------------------------------------------------------------------------------------------------#
    # Create count function to return the number of tasks
    def count(self, type=1):

        # 1: all users, 0: not deleted. -1: deleted
        if type == -1:
            count = self.objects.select_related('taskuser').filter(task_deleted=True, taskuser__user_deleted = False).count()
        elif type == 0:
            count = self.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False).count()
        else:
            count = self.objects.all().count()
        return count
#---------------------------------------------------------------------------------------------------------------------#
    # Create an overview function to collect the statistics of tasks
    def overview(self):
        # The total number of tasks has been generated and tracked using the task_manager.py
        # Total number of completed tasks
        # Total number of uncompleted tasks
        # Total number of overdue tasks 
        # Total number of tasks that haven't been completed and that are overdue
        # The percentage of tasks that are incomplete
        # The percentage of tasks that are overdue

        task_dictionary = {}
        task = self.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False)
        task_dictionary = {
            "total_tasks": task.count(),
            "completed_tasks": self.objects.select_related('taskuser').filter(task_deleted=False, task_completed = True, taskuser__user_deleted = False).count(),
            "uncompleted_tasks": self.objects.select_related('taskuser').filter(task_deleted=False, task_completed = False, taskuser__user_deleted = False).count(),
            "overdue_tasks": self.objects.select_related('taskuser').filter(task_deleted=False, task_completed = False, task_due_date__lte=timezone.now(),  taskuser__user_deleted = False).count(),
            "uncompleted_and_overdue": self.objects.select_related('taskuser').filter(task_deleted=False, task_completed = False, task_due_date__gte=timezone.now(),  taskuser__user_deleted = False).count(),
        } 
        return task_dictionary

#---------------------------------------------------------------------------------------------------------------------#
    # Create query_tasks function to handle the case that the models' Task and TaskUser needed with message and username
    def query_tasks(message, username=None):
        context = {}
        task_queryset = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False).order_by('-task_id')
        user_queryset = TaskUser.objects.filter(user_deleted = False)
        context = {
            "Task": task_queryset,
            "User": user_queryset,
            "Message": message,
            "Username": username,
        }
        return context

#---------------------------------------------------------------------------------------------------------------------#
    # Create view_task function to handle the user's click View All and View Mine, 
    # and then query all users' tasks or my tasks only 
    def view_task(request, type, message=None):
        context = {}
        if type == 0:
            task_queryset = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False, taskuser__user_username = request.session["user_username"] ).order_by('-task_id')
        else:
            task_queryset = Task.objects.select_related('taskuser').filter(task_deleted=False, taskuser__user_deleted = False).order_by('-task_id')
        context = {
            "Task": task_queryset,
            "Message": message,
        }
        return context

