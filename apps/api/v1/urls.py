from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.V1View.as_view(), name='v1_home'),
]
