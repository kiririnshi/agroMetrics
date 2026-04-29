from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Producto(BaseModel):
    nombre = models.CharField(max_length=255)
    variedad = models.CharField(max_length=255, null=True, blank=True)
    calidad = models.CharField(max_length=255, null=True, blank=True)
    unidad_comercio = models.CharField(max_length=255)
    origen = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "variedad", "calidad"],
                name="unique_producto"
            )
        ]

class Region(BaseModel):
    id_region = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=255)

class Mercado(BaseModel):
    nombre = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    sub_sector = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "region"],
                name="unique_mercado"
            )
        ]

class Snapshot(BaseModel):
    fecha = models.DateTimeField()

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    
    precio_minimo = models.DecimalField(max_digits=12, decimal_places=2)
    precio_maximo = models.DecimalField(max_digits=12, decimal_places=2)
    precio_promedio = models.DecimalField(max_digits=12, decimal_places=2)

    volumen = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fecha", "producto", "mercado"],
                name="unique_snapshot"
            )
        ]