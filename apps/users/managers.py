from django.contrib.contenttypes.models import ContentType
from django.db import models


class PermissionManager(models.Manager):
    def get_permissions_for_object(self, name, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(name=name, content_type=content_type, object_id=obj.id).select_related('user')
