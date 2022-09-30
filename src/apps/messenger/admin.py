from django.contrib import admin
from .models import Email,Subscriber,Campaign,Message
from .forms import EmailForm

class EmailAdmin(admin.ModelAdmin):
    model = Email
    add_form = EmailForm



admin.site.register(Email,EmailAdmin)
admin.site.register(Campaign)
admin.site.register(Message)
admin.site.register(Subscriber)
