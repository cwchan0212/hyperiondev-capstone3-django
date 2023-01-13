from django.contrib import admin
from .models import Task, TaskUser

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskUser)