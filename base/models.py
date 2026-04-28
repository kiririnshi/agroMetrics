from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Valores(BaseModel):
    precio_minimo = models.DecimalField(max_digits=20, decimal_places=8)
    precio_maximo = models.DecimalField(max_digits=20, decimal_places=8)
    precio_promedio = models.DecimalField(max_digits=20, decimal_places=8)

class Producto(BaseModel):
    nombre = models.CharField(unique=True, max_length=255)
    variedad = models.CharField(max_length=255)
    calidad = models.CharField(max_length=255)
    unidad_comercio = models.CharField(max_length=255)
    origen = models.CharField(max_length=255)

class Region(BaseModel):
    id_region = models.IntegerField(unique=True)
    nombre = models.CharField(unique=True, max_length=255)

class Mercado(BaseModel):
    nombre = models.CharField(unique=True, max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    sub_sector = models.CharField(max_length=255)

class Snapshot(BaseModel):
    fecha = models.DateTimeField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    valores = models.ForeignKey(Valores, on_delete=models.CASCADE)