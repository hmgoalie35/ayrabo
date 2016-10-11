from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ManagerHomeView.as_view(), name='home'),
]
