from django.db import models
from leagues.models import League


class Division(models.Model):
    name = models.CharField(max_length=128, verbose_name='Name')
    league = models.ForeignKey(League)

    class Meta:
        ordering = ['name']
        unique_together = (
            ('name', 'league'),
        )

    def __str__(self):
        return self.name
