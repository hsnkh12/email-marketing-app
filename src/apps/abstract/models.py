from django.db import models
from django.template.defaultfilters import slugify
import uuid



class UUIDModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SlugModel(models.Model):

    slug = models.SlugField(
        verbose_name = 'Safe URL',
        help_text = 'will be set by default',
        blank = True,
        max_length = 200,
        unique = True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs): 
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)