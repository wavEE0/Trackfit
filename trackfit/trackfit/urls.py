from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("dashboard", views.dashboard, name="dashboard"),
    path('nutrition/', include('nutrition.urls')),
]
