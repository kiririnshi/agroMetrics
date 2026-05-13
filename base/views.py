from datetime import datetime, timezone
from decimal import Decimal
import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto, Snapshot, Region
from .selectors import mercado_list, producto_list, producto_mean_list, region_list
from .serializers import MercadoSerializer, ProductoSerializer, RegionSerializer, SnapshotSerializer


@api_view(['GET'])
def get_regiones(request):
    regiones = region_list()
    serializer = RegionSerializer(regiones, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_mercados_by_region(request):
    region = request.query_params.get('region')
    mercados = mercado_list(region)
    serializer = MercadoSerializer(mercados, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_productos(request):
    productos = producto_list()
    serializer = ProductoSerializer(productos, many=True, fields=["nombre", "variedad", "calidad", "origen"]) # Mandar fields=["algo"] si solo quiero un campo
    return Response(serializer.data)

@api_view(['GET'])
def get_producto_list_by_mean(request):
    producto = request.query_params.get('producto') # ej: arandano
    unidad = request.query_params.get('unidad') # ej: kg
    productos_mean = producto_mean_list(producto, unidad)

    serializer = SnapshotSerializer(productos_mean, many=True)
    return Response(serializer.data)

def get_snapshots(request):
    if (request.method == 'GET'):
        data = serializers.serialize('json', Snapshot.objects.all()[:100])
        return JsonResponse(json.loads(data), safe=False)