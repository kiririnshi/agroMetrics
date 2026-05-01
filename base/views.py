from datetime import datetime, timezone
from decimal import Decimal
import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render

from .models import Producto

def get_productos(request):
    if (request.method == 'GET'):
        data = serializers.serialize('json', Producto.objects.all())
        return JsonResponse(json.loads(data), safe=False)


