from django.db import models
from django.conf import settings 
from django.db.models.fields import CharField
from .managers import BaseFilterManager
from django.urls import reverse
from cryptography.fernet import Fernet
from ..abstract.models import UUIDModel

class Email(UUIDModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )

    email = models.EmailField(
        max_length=60,
        help_text= '@privateemail or @gmail'
    )

    password = models.CharField(
        max_length=500,
        help_text="Your password will be encrypted"
    )

    smtp_server = models.CharField(
        max_length= 60,
        verbose_name= 'Smtp server',
        help_text= 'smtp.domain.com',
        default= 'mail.privateemail.com'
    )

    port = models.CharField(
        default= '587',
        max_length=10,
        verbose_name='Email port'
    )

    tls = models.BooleanField(
        default=True,
        verbose_name= 'Email use TLS'
    )

    objects = BaseFilterManager()

    class Meta:
        ordering = ['id',]
        verbose_name = "Sender's email"
        verbose_name_plural = "Sender's emails"

    def __str__(self):
        return f" User : {self.user.username}  |  Email : {self.email}"

    def save(self, *args, **kwargs):

        

        password = bytes(self.password,'utf-8')
        string_rep = str(self.ecrypt(password))
        self.password = string_rep[2:-1]


        super(Email, self).save(*args, **kwargs)

    def ecrypt(self, password): # need password and return cipher password
        key = settings.KEY
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(password)
        return cipher_text



class Subscriber(models.Model):


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )

    email = models.EmailField(
        max_length=70,
        help_text= '@privateemail or @gmail'
    )

    date_joined = models.DateField(
        blank=True,
        null = True,
        verbose_name= "Date Joined"
    )
    
    objects = BaseFilterManager()

    class Meta:
        ordering = ['date_joined',]

    def __str__(self):
        return f" Related to : {self.user.username}  |  Email : {self.email}"



class Campaign(UUIDModel):

    CHOICES = (
        ('p','Pending...'),
        ('a','Accepted'),
        ('r','Rejected')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        null = True,
        related_name="campaigns_related",
    )

    from_email = models.ForeignKey(
        Email,
        on_delete= models.CASCADE,
        related_name="campaigns_related",
        verbose_name= "Sender's emails",
    )

    to_emails = models.ManyToManyField(
        Subscriber,
        related_name="campaigns_related",
        verbose_name= "To",
    )

    date_sent = models.DateField(
        blank=True,
        null = True,
        verbose_name= "Date sent"
    )

    completed = models.BooleanField(
        default=False
    )

    status = CharField(
        max_length=1,
        default= 'p',
        choices=CHOICES
    )

    objects = BaseFilterManager()

    class Meta:
        ordering = ['-id',]

    # def __str__(self):
    #     return f" Related to : {self.from_email.user}  |  Email used : {self.from_email}  |  Subject : {self.message.subject}"

    def get_absolute_url(self):       
        return reverse('messenger:campaign-detail', args=[str(self.id)])

    

class Message(UUIDModel):

    TYPE_CHOICES = (
        ('h','html'),
        ('p','plain text')
    )

    camp = models.OneToOneField(
        Campaign,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Campaign'
    )

    subject = models.CharField(
        max_length=25,
        default= 'Campaign',
        verbose_name= 'Email subject'
    )

    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES
    )

    body = models.TextField(

    )

    objects = BaseFilterManager()

    def __str__(self):
        return self.subject
        






