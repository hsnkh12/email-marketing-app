
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
import os
from dotenv import load_dotenv
load_dotenv()

urlpatterns = [
    
    path('',TemplateView.as_view(template_name = "home.html"),name="home"),
    
    path('accounts/',include('apps.accounts.urls')),
    path('messenger/',include('apps.messenger.urls')),
    path(os.environ['admin_url'], admin.site.urls),
]
