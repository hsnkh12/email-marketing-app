from django.views.generic.edit import DeleteView
from apps.messenger.models import Email
from django.shortcuts import render,redirect
from django.views.generic import View
from .forms import CreateUserForm,UpdateUserForm
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,)
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .tokens import TokenGenerator
from .models import User
from django.http import HttpResponse
from ..email_sender.celery import send_activation_mail_async_task

class LoginFormView(SuccessMessageMixin, LoginView):
    template_name = 'registration/login.html'
    success_url = '/'
    success_message = "You were successfully logged in"

class RegisterView(View):


    def get(self,request):

        if not request.user.is_authenticated:
            
            form = CreateUserForm()

            context = {"form":form}
            return render(request,"registration/register.html",context)

        messages.warning(self.request,"You already logged in!")
        return redirect("/")


    def post(self,request):
        
        form = CreateUserForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_activation_mail_async_task.delay(userID=str(user.id))

            return render(request,"registration/wait_email_confirmation.html",)

        
        context = {"form":form}
        return render(request,"registration/register.html",context)

def ActivateEmailView(request, uidb64, token):

    account_activation_token = TokenGenerator()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/email_confirmed.html')
    else:
        return HttpResponse('Activation link is invalid!')


class ProfileView(LoginRequiredMixin,UpdateView):
    
    form_class = UpdateUserForm
    template_name="registration/profile.html"

    def get_success_url(self): 

        messages.success(self.request,"Updated succesfully")
        return "/accounts/profile/"

    def get_object(self):
        return self.request.user



class DeleteAccountView(LoginRequiredMixin,DeleteView):
    

    template_name = 'registration/delete_acc.html'
    
    def get_success_url(self):
        return '/accounts/register/'

    def get_object(self):
        return self.request.user