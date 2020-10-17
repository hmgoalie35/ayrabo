from django.db import IntegrityError
from rest_framework import serializers, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from api.mixins import BulkCreateMixin, BulkDeleteMixin, BulkUpdateMixin, BulkViewActionMixin, DynamicSerializerMixin
from api.serializers import (
    AbstractBulkCreateModelSerializer,
    AbstractBulkDeleteModelSerializer,
    AbstractBulkUpdateModelSerializer,
)
from ayrabo.utils.testing import BaseAPITestCase
from ayrabo.utils.testing.models import DummyModel


class DummyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyModel
        fields = ('id', 'name', 'count')


class BulkCreateDummyModelSerializer(AbstractBulkCreateModelSerializer):
    """A simple serializer solely used for testing"""

    class Meta(AbstractBulkCreateModelSerializer.Meta):
        model = DummyModel
        fields = ('id', 'name', 'count')


class BulkUpdateDummyModelSerializer(AbstractBulkUpdateModelSerializer):
    """A simple serializer solely used for testing"""

    class Meta(AbstractBulkUpdateModelSerializer.Meta):
        model = DummyModel
        fields = ('id', 'name', 'count')


class BulkDeleteDummyModelSerializer(AbstractBulkDeleteModelSerializer):
    """A simple serializer solely used for testing"""

    class Meta(AbstractBulkDeleteModelSerializer.Meta):
        model = DummyModel


class DynamicSerializerMixinViewSet(DynamicSerializerMixin, viewsets.GenericViewSet):
    serializer_class = DummyModelSerializer
    serializer_class_mappings = {'bulk_create': BulkCreateDummyModelSerializer}


class BulkViewActionMixinViewSet(BulkViewActionMixin, viewsets.GenericViewSet):
    serializer_class = DummyModelSerializer
    serializer_class_mappings = {'bulk_create': BulkCreateDummyModelSerializer}


class DummyModelViewSet(BulkViewActionMixin, BulkCreateMixin, BulkUpdateMixin, BulkDeleteMixin, viewsets.ModelViewSet):
    queryset = DummyModel.objects.all()
    serializer_class = DummyModelSerializer
    serializer_class_mappings = {
        'bulk_create': BulkCreateDummyModelSerializer,
        'bulk_update': BulkUpdateDummyModelSerializer,
        'bulk_delete': BulkDeleteDummyModelSerializer,
    }


class DynamicSerializerMixinTests(BaseAPITestCase):
    def test_get_serializer_class(self):
        view = DynamicSerializerMixinViewSet()

        view.action = 'create'
        # For some reason assertIs(type(...), DummyModelSerializer) isn't working
        self.assertEqual(view.get_serializer_class().__name__, 'DummyModelSerializer')

        view.action = 'bulk_create'
        self.assertEqual(view.get_serializer_class().__name__, 'BulkCreateDummyModelSerializer')


class BulkViewActionMixinTests(BaseAPITestCase):

    def test_validate_bulk_action_data(self):
        view = BulkViewActionMixinViewSet()
        view.action = 'bulk_create'

        view.validate_bulk_action_data([{i: i} for i in range(20)])

        with self.assertRaisesMessage(ValidationError, 'Bulk actions must receive data as a list of items.'):
            view.validate_bulk_action_data({})

        with self.assertRaisesMessage(ValidationError, 'Bulk actions only support 50 items at a time.'):
            view.validate_bulk_action_data([{i: i} for i in range(100)])

    def test_get_serializer(self):
        view = BulkViewActionMixinViewSet()
        view.action = 'bulk_create'
        view.request = None
        view.format_kwarg = None

        # data is a list
        serializer = view.get_serializer(None, data=[{'id': 1}, {'id': 2}])
        self.assertTrue(serializer.many)
        self.assertFalse(serializer.allow_empty)

        # data is missing
        serializer = view.get_serializer(None)
        self.assertFalse(hasattr(serializer, 'many'))
        self.assertFalse(hasattr(serializer, 'allow_empty'))

        # data is not a list
        serializer = view.get_serializer(None, data=(1, 2, 3))
        self.assertFalse(hasattr(serializer, 'many'))
        self.assertFalse(hasattr(serializer, 'allow_empty'))


class BulkCreateMixinTests(BaseAPITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DummyModelViewSet.as_view(actions={'post': 'bulk_create'})

    def test_transaction_atomic(self):
        self.assertEqual(DummyModel.objects.count(), 0)

        # Invalid since name has a unique constraint
        request = self.factory.post('testing', [{'name': 'test123', 'count': 1000}, {'name': 'test123', 'count': 0}])
        # It's actually kind of hard to test this because unit tests are also wrapped in transactions so we have a
        # transaction in a transaction. Removing the @transaction.atomic decorator from the action will cause this unit
        # test to fail, I think that's good enough
        with self.assertRaises(IntegrityError):
            self.view(request)
        self.assertEqual(DummyModel.objects.count(), 0)

    def test_invalid_post(self):
        # Request data is not a list
        request = self.factory.post('testing', {})
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions must receive data as a list of items.')

        # Request data is an empty list
        request = self.factory.post('testing', [])
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors[0]), 'This list may not be empty.')

        # Request data exceeds number of max items
        request = self.factory.post(
            'testing',
            data=[{'name': i, 'count': i} for i in range(BulkViewActionMixin.BULK_ACTION_MAX_ITEMS + 5)]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions only support 50 items at a time.')

        # Request data missing required fields
        request = self.factory.post(
            'testing',
            data=[{'name': 'Scarn'}, {'name': 'Schrute', 'count': 1}]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)

        err1 = response.data[0]
        err2 = response.data[1]

        self.assertEqual(str(err1.get('count')[0]), 'This field is required.')
        self.assertDictEqual(err2, {})

        self.assertEqual(DummyModel.objects.count(), 0)

    def test_valid_post(self):
        request = self.factory.post(
            'testing',
            data=[{'name': f'Obj {i}', 'count': i} for i in range(5)]
        )
        response = self.view(request)
        response.render()

        obj = response.data[0]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(DummyModel.objects.count(), 5)
        self.assertEqual(obj.get('name'), 'Obj 0')
        self.assertEqual(obj.get('count'), 0)


class BulkUpdateMixinTests(BaseAPITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DummyModelViewSet.as_view(actions={'post': 'bulk_update'})
        self.instance1 = DummyModel.objects.create(name='Instance 1', count=1)
        self.instance2 = DummyModel.objects.create(name='Instance 2', count=2)

    def test_transaction_atomic(self):
        # It's hard to test this because I don't know how to intentionally cause the db transaction to fail
        # Gonna keep this here as a stub
        pass

    def test_invalid_post(self):
        # Request data is not a list
        request = self.factory.post('testing', {})
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions must receive data as a list of items.')

        # Request data is an empty list
        request = self.factory.post('testing', [])
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors[0]), 'This list may not be empty.')

        # Request data exceeds number of max items
        request = self.factory.post(
            'testing',
            data=[{'name': i, 'count': i} for i in range(BulkViewActionMixin.BULK_ACTION_MAX_ITEMS + 5)]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions only support 50 items at a time.')

        # Id DNE
        request = self.factory.post(
            'testing',
            data=[{'id': 1000, 'count': 100}, {'id': self.instance2.id, 'name': 'Scarn'}]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data[0].get('id')[0]), "Invalid pk \"1000\" - object does not exist.")
        self.assertDictEqual(response.data[1], {})

        # Request data missing required fields
        request = self.factory.post(
            'testing',
            data=[{'id': self.instance1.id, 'name': ''}, {'id': self.instance2.id, 'count': None}, {}]
        )
        response = self.view(request)
        response.render()

        self.assertEqual(response.status_code, 400)

        err1 = response.data[0]
        err2 = response.data[1]
        err3 = response.data[2]

        self.assertEqual(str(err1.get('name')[0]), 'This field may not be blank.')
        self.assertEqual(str(err2.get('count')[0]), 'This field may not be null.')
        self.assertEqual(str(err3.get('id')[0]), 'This field is required.')

    def test_valid_post(self):
        request = self.factory.post(
            'testing',
            data=[
                # This one is testing a partial update
                {'id': self.instance1.id, 'name': 'MScarn'},
                {'id': self.instance2.id, 'name': 'JHalp', 'count': 44}
            ]
        )
        response = self.view(request)
        response.render()

        obj = response.data[1]

        self.assertEqual(response.status_code, 200)
        # Make sure the response includes updated data
        self.assertEqual(obj.get('name'), 'JHalp')
        self.assertEqual(obj.get('count'), 44)
        # Make sure objs actually got updated
        self.instance1.refresh_from_db()
        self.instance2.refresh_from_db()
        self.assertEqual(self.instance1.name, 'MScarn')
        self.assertEqual(self.instance1.count, 1)
        self.assertEqual(self.instance2.name, 'JHalp')
        self.assertEqual(self.instance2.count, 44)


class BulkDeleteMixinTests(BaseAPITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DummyModelViewSet.as_view(actions={'post': 'bulk_delete'})
        self.instance1 = DummyModel.objects.create(name='Instance 1', count=1)
        self.instance2 = DummyModel.objects.create(name='Instance 2', count=2)

    def test_transaction_atomic(self):
        # It's hard to test this because I don't know how to intentionally cause the db transaction to fail
        # Gonna keep this here as a stub
        pass

    def test_invalid_post(self):
        # Request data is not a list
        request = self.factory.post('testing', {})
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions must receive data as a list of items.')

        # Request data is an empty list
        request = self.factory.post('testing', [])
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors[0]), 'This list may not be empty.')

        # Request data exceeds number of max items
        request = self.factory.post(
            'testing',
            data=[{'id': i} for i in range(BulkViewActionMixin.BULK_ACTION_MAX_ITEMS + 5)]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        non_field_errors = response.data.get('non_field_errors')
        self.assertEqual(str(non_field_errors), 'Bulk actions only support 50 items at a time.')

        # Id DNE
        request = self.factory.post(
            'testing',
            data=[{'id': 1000}, {'id': self.instance2.id}]
        )
        response = self.view(request)
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(str(response.data[0].get('id')[0]), "Invalid pk \"1000\" - object does not exist.")
        self.assertDictEqual(response.data[1], {})

        # Request data missing required fields
        request = self.factory.post(
            'testing',
            data=[{'id': None}, {'id': ''}]
        )
        response = self.view(request)
        response.render()

        self.assertEqual(response.status_code, 400)

        err1 = response.data[0]
        err2 = response.data[1]

        self.assertEqual(str(err1.get('id')[0]), 'This field may not be null.')
        self.assertEqual(str(err2.get('id')[0]), 'This field may not be null.')

    def test_valid_post(self):
        request = self.factory.post(
            'testing',
            data=[{'id': self.instance1.id}, {'id': self.instance2.id}]
        )
        response = self.view(request)
        response.render()

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.data)
        self.assertEqual(DummyModel.objects.count(), 0)
