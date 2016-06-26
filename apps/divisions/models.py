from django.db import models
from leagues.models import League


class Division(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='Name')
    league = models.ForeignKey(League)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
