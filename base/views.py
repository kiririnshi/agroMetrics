from datetime import datetime, timezone
from decimal import Decimal
import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto, Snapshot
from .selectors import producto_list, producto_mean_list
from .serializers import ProductoSerializer

@api_view(['GET'])
def get_productos_all(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_producto_list(request):
    productos = producto_list().values('nombre')
    serializer = ProductoSerializer(productos, many=True, fields=["nombre"])
    return Response(serializer.data)

@api_view(['GET'])
def get_producto_list_by_mean(request):
    productos_mean = producto_mean_list()
    breakpoint("view")

def get_snapshots(request):
    if (request.method == 'GET'):
        data = serializers.serialize('json', Snapshot.objects.all()[:100])
        return JsonResponse(json.loads(data), safe=False)