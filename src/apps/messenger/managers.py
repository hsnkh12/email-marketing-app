from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404



class BaseFilterManager(models.Manager):


    def filter_by(self,*args,**kwargs):

        return self.select_related(*args).filter( **kwargs )

    
    def get_or_404(self,*args,**kwargs):

        
        return self.select_related(*args).get(**kwargs)
        



    