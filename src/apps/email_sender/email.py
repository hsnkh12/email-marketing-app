from django.core.mail import send_mail
from cryptography.fernet import Fernet
from django .conf import settings
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from ..accounts.tokens import TokenGenerator
from django.utils.encoding import force_bytes
from django.apps import apps


def send_activation_mail(**kwargs):

    UserModel = apps.get_model('accounts','User')
    user = UserModel.objects.get(pk=kwargs['userID'])
    account_activation_token = TokenGenerator()

    context = {
        'user':user, 
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user)
        }

    html_content = render_to_string('mail/email_confirm.html',context)

    mail = {
        'subject' : "Sendthro Email Confirmation",
        'message' : None,
        'html_message' : html_content,
        'from_email' : settings.EMAIL_HOST_USER,
    }

    send_mail(**mail,fail_silently=True, recipient_list= [user.email])

    return


def get_password(password):

    key = settings.KEY
    f = Fernet(key)

    password = f.decrypt(str.encode(password))
    return password.decode()



def send_mail_from_to(camp_id):

    Campaign = apps.get_model('messenger' , 'Campaign')
    camp = Campaign.objects.get( id = camp_id)

    kwargs = {
        'subject' : camp.message.subject,
        'body' : camp.message.body,
        'from_email' : camp.from_email.email,
        'password' : camp.from_email.password,
        'to': [ sub.email for sub in camp.to_emails.all() ],
        'smtp' : camp.from_email.smtp_server,
        'port' : camp.from_email.port,
        'tls' : camp.from_email.tls
    }

    

    try:
        email = kwargs['from_email']

        settings.EMAIL_PORT = int(kwargs['port'])
        settings.EMAIL_HOST = kwargs['smtp'] 
        settings.EMAIL_USE_TLS = kwargs['tls']

        passwordEnc = kwargs['password']

        html_content = render_to_string('mail/message.html', { 'html' : kwargs['body'] })

        mail = {
            'subject' : kwargs['subject'],
            'html_message' : html_content,
            'message' : None,
            'auth_user' :  email,
            'from_email' : email,
            'auth_password': get_password(passwordEnc),

        }

        for sub in kwargs['to']:

            send_mail(**mail, recipient_list= [sub])

        camp.status = 'a'

    except:
        

        camp.status = 'r'
    
    camp.save()
    






    





