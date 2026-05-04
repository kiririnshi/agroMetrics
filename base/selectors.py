
from django.db.models import Avg, Count, QuerySet
from .models import Producto, Snapshot

def producto_list() -> QuerySet[Producto]:
    return Producto.objects.all().distinct().order_by('nombre') 

def producto_nombre_unidad_list() -> QuerySet[Producto]:
    return Producto.objects.all()

def producto_mean_list():
    productos = producto_list()
    #for q in productos:
        #snapshots = Snapshot.objects.filter(producto=q).annotate(promedio = Avg('precio_promedio'))
        # ss = Snapshot.objects.filter(producto=q).values('precio_promedio').annotate(dcount = Avg('precio_promedio')).order_by('precio_promedio') 
        #snapshots = Snapshot.objects.filter()
    resultado = Snapshot.objects.filter(
        producto__in=productos
    ).aggregate(promedio=Avg('precio_promedio'))
    
    mean_list = Snapshot.objects.filter()
    return mean_list