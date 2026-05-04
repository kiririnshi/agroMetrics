from django.urls import path

from . import views

urlpatterns = [
    path('get_productos/', views.get_productos_all),
    path('get_productos_nombres/', views.get_producto_list),
    path('get_producto_list_by_mean', views.get_producto_list_by_mean),
    path('get_snapshots/', views.get_snapshots),
]