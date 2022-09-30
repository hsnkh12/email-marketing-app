from django.db import models
from django.contrib.auth.models import AbstractUser
from ..messenger.models import Subscriber
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = models.CharField(max_length=10,primary_key=False, null=True, blank=True)

    email = models.EmailField(
        max_length= 60,
        unique= True,
        help_text="@privateemail or @gmail"
    )

    bio = models.TextField(
        blank= True,
        null = True,
        help_text= "Optional",
        verbose_name= "Form's Bio",
        default="Hello my name is..."
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]




@receiver(post_save, sender=User)
def create_user_subscriber(sender, instance, created, **kwargs):
    if created:
        Subscriber.objects.create(user=instance, email=instance.email , date_joined = timezone.now().date() )