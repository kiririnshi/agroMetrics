from django.urls import path

from . import views

urlpatterns = [
    path('get_productos/', views.get_productos_all),
    path('get_productos_nombres/', views.get_productos_nombres),
    path('get_snapshots/', views.get_snapshots),
]