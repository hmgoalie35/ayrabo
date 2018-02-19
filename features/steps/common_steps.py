from behave import *
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from common.tests import GenericChoiceFactory


@step('The following generic choice objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        model_cls = apps.get_model(data.pop('content_type'))
        data['object_id'] = model_cls.objects.first().id
        data['content_type'] = ContentType.objects.get_for_model(model_cls)
        obj_id = data.pop('id', None)
        if obj_id:
            data['id'] = obj_id
        GenericChoiceFactory(**data)
