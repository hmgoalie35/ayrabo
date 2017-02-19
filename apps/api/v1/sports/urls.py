from django.conf.urls import url, include

from . import views

sport_urls = []

sport_registration_urls = [
    url(r'^(?P<pk>\d+)/(?P<role>(coach|player|referee|manager))/remove/$',
        views.RemoveSportRegistrationRoleAPIView.as_view(), name='remove_role'),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
