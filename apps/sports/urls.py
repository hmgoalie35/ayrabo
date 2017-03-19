from django.conf.urls import url, include

from . import views

sport_urls = []

sport_registration_urls = [
    url(r'^create/$', views.CreateSportRegistrationView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', views.SportRegistrationDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/(?P<role>(coach|player|referee|manager))/add/$', views.AddSportRegistrationRoleView.as_view(),
        name='add_role'),

    url(r'^(?P<pk>\d+)/players/', include('players.urls', namespace='players')),
    url(r'^(?P<pk>\d+)/coaches/', include('coaches.urls', namespace='coaches')),
    url(r'^(?P<pk>\d+)/referees/', include('referees.urls', namespace='referees')),
    url(r'^(?P<pk>\d+)/managers/', include('managers.sport_registration_urls', namespace='managers')),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
