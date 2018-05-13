from factory import django, Sequence, post_generation

from organizations.models import Organization


class OrganizationFactory(django.DjangoModelFactory):
    name = Sequence(lambda x: 'Organization {}'.format(x))

    class Meta:
        model = Organization

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        self.full_clean(exclude=['slug'])
