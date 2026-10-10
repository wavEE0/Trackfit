from django.urls import path, include
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("nutrition/", include("nutrition.urls")),
]

if settings.DEBUG:
    from .test_views import e2e_test_login
    urlpatterns += [path("e2e-login/", e2e_test_login, name="e2e_test_login")]
