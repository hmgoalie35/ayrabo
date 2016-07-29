from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create/$', views.CreateUserProfileView.as_view(), name='create'),
    url(r'^select-roles/$', views.SelectRolesView.as_view(), name='select_roles'),
    url(r'^finish/$', views.FinishUserProfileView.as_view(), name='finish'),
    url(r'^edit/$', views.UpdateUserProfileView.as_view(), name='update'),
]
