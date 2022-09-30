from django.urls import path,include
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from .views import RegisterView,ProfileView,DeleteAccountView,LoginFormView,ActivateEmailView

app_name = 'accounts'

urlpatterns = [

    path("register/",RegisterView.as_view(),name="register"),
    path("login/",LoginFormView.as_view(),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("profile/",ProfileView.as_view(),name="profile"),
    path("activate/<uidb64>/<token>",ActivateEmailView,name="activate"),
    path("account-delete/",DeleteAccountView.as_view(),name="account-delete"),


    
]