from django.urls import path
from . import views

urlpatterns = [
    path("recommendation/", views.recommendation, name="recommendation"),
    path("tracking/", views.tracking, name="tracking"),
    path('add-daily-intake/', views.add_daily_intake, name='add_daily_intake'),
    path('remove-daily-intake/', views.remove_daily_intake, name='remove_daily_intake'),
    path("add-custom-meal/", views.add_custom_meal, name="add_custom_meal"),
    path("remove-custom-meal/", views.remove_custom_meal, name="remove_custom_meal"),
    path("add-custom-food/", views.add_custom_food, name="add_custom_food"),
    path("remove-custom-food/", views.remove_custom_food, name="remove_custom_food"),
]