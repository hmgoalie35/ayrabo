from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^registration/new/$', views.CreateSportRegistrationView.as_view(), name='create_sport_registration'),
    url(r'^registration/finish/$', views.FinishSportRegistrationView.as_view(), name='finish_sport_registration'),

]
