from django.conf.urls import url, include

from . import views

sport_urls = []

sport_registration_urls = [
    url(r'^create/$', views.CreateSportRegistrationView.as_view(), name='create_sport_registration'),
    url(r'^finish/$', views.FinishSportRegistrationView.as_view(), name='finish_sport_registration'),
    url(r'^(?P<pk>\d+)/update/$', views.UpdateSportRegistrationView.as_view(),
        name='update_sport_registration'),
    url(r'^(?P<pk>\d+)/(?P<role>(coach|player|referee|manager))/add/$',
        views.AddSportRegistrationRoleView.as_view(), name='add_sport_registration_role'),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls)),
    url(r'^sport-registrations/', include(sport_registration_urls)),
]
