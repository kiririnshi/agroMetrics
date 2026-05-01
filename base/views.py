from datetime import datetime, timezone
from decimal import Decimal
import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto, Snapshot
from .serializers import ProductoSerializer

@api_view(['GET'])
def get_productos_all(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_productos_nombres(request):
    productos = Producto.objects.all().values('nombre').distinct().order_by('nombre')
    serializer = ProductoSerializer(productos, many=True, fields=["nombre"])
    return Response(serializer.data)

#def get_productos_nombres(request):
#    if (request.method == 'GET'):
#        data = serializers.serialize('json', Producto.objects.all().values('nombre'))
#        return JsonResponse(json.loads(data), safe=False)

def get_snapshots(request):
    if (request.method == 'GET'):
        data = serializers.serialize('json', Snapshot.objects.all()[:100])
        return JsonResponse(json.loads(data), safe=False)