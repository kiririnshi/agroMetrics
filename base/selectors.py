
from django.db.models import Avg, Count, QuerySet
from .models import Mercado, Producto, Region, Snapshot, Unidad

def get_region(name) -> QuerySet[Region]: # Podria ser por nombre o id_region
    return Region.objects.filter(nombre=name)

def get_unidad(unidad) -> QuerySet[Unidad]: # Podria ser por nombre o id_region
    return Unidad.objects.filter(unidad=unidad)

def get_mercado(name) -> QuerySet[Mercado]: # Podria ser por region, nombre o sub_sector
    return Mercado.objects.filter(nombre=name)

def get_producto(name) -> QuerySet[Producto]: # Podria ser por region, nombre o sub_sector
    return Producto.objects.filter(nombre__contains=name)

def mercado_list(region) -> QuerySet[Mercado]:
    return Mercado.objects.filter(region__id_region = region)

def producto_list() -> QuerySet[Producto]:
    return Producto.objects.all().distinct().order_by('nombre') 

def region_list() -> QuerySet[Region]:
    return Region.objects.all().order_by('id_region')

def producto_nombre_unidad_list() -> QuerySet[Producto]:
    return Producto.objects.all()

def producto_mean_list(producto, unidad) -> list: # {'promedio': Decimal('5563.2853906820505331')}
    #productos = producto_list()
    #for q in productos:
        #snapshots = Snapshot.objects.filter(producto=q).annotate(promedio = Avg('precio_promedio'))
        # ss = Snapshot.objects.filter(producto=q).values('precio_promedio').annotate(dcount = Avg('precio_promedio')).order_by('precio_promedio') 
        #snapshots = Snapshot.objects.filter()


    # El usuario deberia elegir el producto y la unidad desde donde quiere sacar la query

    productos = get_producto(producto)
    kilos = get_unidad(unidad)
    
    resultado = Snapshot.objects.filter(
        producto__in = productos,
        unidad__in = kilos 
    )
    #.aggregate(promedio=Avg('precio_promedio'))
    
    return resultado