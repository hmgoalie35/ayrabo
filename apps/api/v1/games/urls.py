from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register('players', views.GamePlayerViewSet, basename='players')

app_name = 'games'
urlpatterns = [
    url(r'^(?P<game_pk>\d+)/', include(router.urls)),
]
