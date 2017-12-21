from django.contrib.contenttypes.models import ContentType
from django.db import models


class ActiveManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(is_active=True)

    def inactive(self):
        return self.get_queryset().filter(is_active=False)


class GenericChoiceManager(models.Manager):
    def get_choices(self, model_cls=None, instance=None):
        """
        Retrieve GenericChoices for the given model class and/or instance.

        :param model_cls: Used to compute the content type.
        :param instance: Used for object_id. instance.pk will be used.
        :return: Filtered queryset containing GenericChoices for the given model class and/or instance.
        """
        if model_cls is None and instance is None:
            raise ValueError('You must specify model_cls or instance')

        content_type = ContentType.objects.get_for_model(model_cls or instance)
        filter_kwargs = {'content_type': content_type}
        qs = self.get_queryset()
        if instance is not None:
            filter_kwargs.update({'object_id': instance.pk})
        return qs.filter(**filter_kwargs)
