from django.db import models
from django.utils.text import slugify


class Sport(models.Model):
    name = models.CharField(max_length=256, unique=True, error_messages={'unique': 'Sport with this name already exists (case-insensitive)'})
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super(Sport, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
