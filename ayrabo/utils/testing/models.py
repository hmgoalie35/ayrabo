from django.db import models


class TestingModel(models.Model):
    class Meta:
        app_label = 'testing'
        abstract = True


class DummyModel(TestingModel):
    name = models.CharField(max_length=255, unique=True)
    count = models.IntegerField()
