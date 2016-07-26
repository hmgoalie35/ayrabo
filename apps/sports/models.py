from django.db import models
from django.utils.text import slugify


class Sport(models.Model):
    name = models.CharField(max_length=256, unique=True,
                            error_messages={'unique': 'Sport with this name already exists (case-insensitive)'})
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        self.save()

    def __str__(self):
        return self.name
