from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin 
from.forms import CreateUserForm
# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CreateUserForm

admin.site.register(User,CustomUserAdmin)