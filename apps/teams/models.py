from django.db import models

from divisions.models import Division


class Team(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    website = models.URLField(max_length=255, verbose_name='Website', null=True, blank=True,
                              help_text='You must include http:// or https://')
    division = models.ForeignKey(Division)

    """
    The fields below are not really necessary to store in this model for the MVP, a link to the team's website would
    provide all of this info and more. However, in the future it might be useful to add fields like below to this model
    or even create a TeamInfo model

    rink - ManyToManyField to a new model Rink which stores various info
    president - CharField
    governor - CharField, should be optional?
    office_address - CharField
    office_phone - CharField
    """

    class Meta:
        ordering = ['name', 'division']
        unique_together = (('name', 'division'),)

    def __str__(self):
        return '{division} - {name}'.format(division=self.division.name, name=self.name)
