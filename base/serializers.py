from rest_framework import serializers
from .models import Mercado, Producto, Region

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            for field in set(self.fields) - allowed:
                self.fields.pop(field)

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id_region', 'nombre']

class MercadoSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(
        read_only=True,
        slug_field='nombre'  # Quiero mostrar este camnpo del modelo Region
    )

    class Meta:
        model = Mercado
        fields = ['nombre', 'sub_sector', 'region']