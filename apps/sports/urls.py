from django.conf.urls import url

from .views import CreateSportView

urlpatterns = [
    url(r'^create/$', CreateSportView.as_view(), name='create_sport'),
]
