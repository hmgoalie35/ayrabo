from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^registration/(?P<pk>\d+)/(?P<role>(coach|player|referee|manager))/remove/$',
        views.RemoveSportRegistrationRoleAPIView.as_view(), name='remove_sport_registration_role'),
]
