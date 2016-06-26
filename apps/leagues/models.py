from django.db import models
from sports.models import Sport


class League(models.Model):
    full_name = models.CharField(max_length=256, unique=True, verbose_name='Full Name',
                                 error_messages={'unique': 'League with this name already exists'})
    abbreviated_name = models.CharField(max_length=32, verbose_name='Abbreviated Name')
    sport = models.ForeignKey(Sport, verbose_name='Sport')

    class Meta:
        ordering = ['full_name']

    def save(self, *args, **kwargs):
        # Takes the first letter of each word and concatenates them together. ex: National Hockey League --> NHL
        words = self.full_name.split(' ')
        self.abbreviated_name = ''.join([word[:1].strip().upper() for word in words])
        super(League, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name
