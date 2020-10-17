from django.db import transaction
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings


class DynamicSerializerMixin:
    """
    Mixin that chooses the appropriate serializer based on the viewset action. Only supports viewset actions as of now.
    Use this mixin with all viewset classes and when we add support, all drf api views.
    """
    serializer_class_mappings = {}

    def get_serializer_class(self):
        """
        Compute the serializer class for the given viewset action, defaulting to the default DRF behavior if no mapping
        has been defined.
        """
        return self.serializer_class_mappings.get(self.action, super().get_serializer_class())


class BulkViewActionMixin(DynamicSerializerMixin):
    """
    Mixin providing shared bulk action functionality. Use this mixin with all viewset or class based api views.
    """
    BULK_ACTION_MAX_ITEMS = 50

    def validate_bulk_action_data(self, data):
        """
        Validates:

        The request payload is a list of items

        The request payload contains less than the bulk action max items. This prevents abuse of the bulk endpoints
        (which could bring down our servers/database) and facilitates faster api response times since we're processing
        fewer records.

        :param data: Data from the request
        """
        key = api_settings.NON_FIELD_ERRORS_KEY

        if not isinstance(data, list):
            raise serializers.ValidationError({key: 'Bulk actions must receive data as a list of items.'})

        if len(data) > self.BULK_ACTION_MAX_ITEMS:
            raise serializers.ValidationError({
                key: f'Bulk actions only support {self.BULK_ACTION_MAX_ITEMS} items at a time.'
            })

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs.update({'many': True, 'allow_empty': False})
        return super().get_serializer(*args, **kwargs)


class BulkCreateMixin:
    """Bulk create model instances in an atomic transaction."""

    @transaction.atomic()
    @action(detail=False, methods=['post'], url_path='bulk/create')
    def bulk_create(self, request):
        self.validate_bulk_action_data(data=request.data)
        # Bulk create is already supported by DRF
        return self.create(request)


class BulkUpdateMixin:
    """Bulk update model instances in an atomic transaction."""

    @transaction.atomic()
    @action(detail=False, methods=['post'], url_path='bulk/update')
    def bulk_update(self, request):
        self.validate_bulk_action_data(data=request.data)
        # TODO Permissions, can even update the objs?
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.bulk_update()
        return Response(serializer.data)


class BulkDeleteMixin:
    """Bulk delete model instances in an atomic transaction."""

    @transaction.atomic()
    @action(detail=False, methods=['post'], url_path='bulk/delete')
    def bulk_delete(self, request):
        self.validate_bulk_action_data(data=request.data)
        # TODO Permissions, can even delete the objs?
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.bulk_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
