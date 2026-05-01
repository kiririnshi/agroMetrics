from django.urls import path

from . import views

urlpatterns = [
    path('get_productos/', views.get_productos),
]