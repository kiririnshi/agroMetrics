from django.urls import path

from . import views

urlpatterns = [
    path('get_productos/', views.get_productos),
    path('get_regiones/', views.get_regiones),
    #path('get_productos_nombres/', views.get_producto_list),
    path('get_producto_list_by_mean', views.get_producto_list_by_mean),
    path('get_snapshots/', views.get_snapshots),
]