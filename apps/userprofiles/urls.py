from django.conf.urls import url

from .views import CreateUserProfileView, UpdateUserProfileView, FinishUserProfileView

urlpatterns = [
    url(r'^create/$', CreateUserProfileView.as_view(), name='create'),
    url(r'^finish/$', FinishUserProfileView.as_view(), name='finish'),
    url(r'^edit/$', UpdateUserProfileView.as_view(), name='update'),
]
