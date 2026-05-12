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
from .serializers import MercadoSerializer, ProductoSerializer, RegionSerializer


@api_view(['GET'])
def get_regiones(request):
    regiones = region_list().values('id_region', 'nombre')
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
    productos = producto_list().values('nombre')
    serializer = ProductoSerializer(productos, many=True, fields=["nombre"])
    return Response(serializer.data)

@api_view(['GET'])
def get_producto_list_by_mean(request):
    productos_mean = producto_mean_list()
    # {'promedio': Decimal('5563.2853906820505331')}
    return JsonResponse()

#@api_view(['GET'])
#def get_snapshot_by_region_or_product(request):




def get_snapshots(request):
    if (request.method == 'GET'):
        data = serializers.serialize('json', Snapshot.objects.all()[:100])
        return JsonResponse(json.loads(data), safe=False)