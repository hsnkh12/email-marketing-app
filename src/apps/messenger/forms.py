from django import forms
from django.forms import widgets
from .models import Email,Subscriber



class EmailForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:

        model = Email
        fields = ['email','password','smtp_server','port','tls']

    

class SubscriberForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        fields = ['email']



