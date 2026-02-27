from rest_framework import serializers
from ..models import Products, Brand, Category, Valorations, Comments
from django.db import transaction
from django.db.models import Avg,Sum,Count
from django.forms import widgets
import re

##### PRODUCTS REGISTER SERIALIZER
#
# Este módulo contiene serializers para crear y validar los modelos de productos,
# categorías, marcas, valoraciones y comentarios. Cada clase dispone de un
# docstring descriptivo para que drf-spectacular pueda documentar correctamente
# el esquema.

class ProductRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para el alta y la edición de productos.

    Valida nombre único, precios dentro de rango, stock y formato de imagen.
    """
    id = serializers.ReadOnlyField()
    name_product = serializers.CharField(
        label = 'Producto',
        style = {'placeholder':'Escribe el nombre del producto'},
        required = True,
        trim_whitespace = True
    )
    category_product = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar categoria',
        queryset = Category.objects.all()
    )
    category = serializers.ReadOnlyField(source = 'category_product.name_category')
    brand_product = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar marca',
        queryset = Brand.objects.all()
    )
    brand = serializers.ReadOnlyField(source = 'brand_product.name_brand')
    price_product = serializers.DecimalField(
        label = 'Precio',
        style = {'placeholder':'Escribe el precio'},
        default = 1,
        max_digits=12,
        decimal_places=2
    )
    stock_product =serializers.IntegerField(
        label = 'Stock',
        style ={'placeholder':'Escribe el stock'},
        default = 1
    )
    image_product = serializers.ImageField(
        label = 'Imagen de producto',
        style = {'help_text':'Solo se admiten imagenes PNG'}
    )
    class Meta:
        model = Products
        fields = ['id','name_product','category_product', 'category','brand_product','brand','price_product','stock_product', 'image_product']
    def validate_name_product(self, value):
        product_obj = value.upper().strip()
        queryset = Products.objects.filter(name_product = product_obj)
        errors = []
        letter_count = 0
        if len(product_obj)< 3:
            errors.append('El nombre del producto debe tener al menos 3 caracteres')
        if re.search(r'[^a-zA-Z0-9\s\-\.\.ñÑ]', product_obj):
            errors.append('El nombre del producto contiene caracteres no válidos')
        for letter in product_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El nombre del producto debe tener al menos 3 letras')
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            errors.append('El nombre del producto ingresado ya existe en la base de datos')
        if errors:
            raise serializers.ValidationError(errors)
        return product_obj
    def validate_price_product(self, value):
        price_obj = value
        errors = []
        if price_obj is None:
            errors.append('Por favor ingrese un precio para el producto')
        if price_obj < 1:
            errors.append('El precio del producto debe ser mayor a 1')
        if price_obj >99999999:
            errors.append('El precio del producto excede el maximo permitido')
        if errors:
            raise serializers.ValidationError(errors)
        return price_obj
    def validate_stock_product(self, value):
        stock_obj = value
        errors =[]
        if stock_obj is None:
            errors.append('Por favor ingrese un stock para el producto')
        if stock_obj < 1:
            errors.append('El stock debe ser mayor a 0')
        if stock_obj > 99999:
            errors.append('El stock ingresado excede el maximo permitido')
        if errors:
            raise serializers.ValidationError(errors)
        return stock_obj
    def validate_image_product(self, value):
        image_obj = value
        allow_content = ['image/png']
        errors = []
        if image_obj:
            if image_obj.content_type not in allow_content:
                errors.append('Formato de imagen no válido, solo se admite PNG')
            if image_obj.size > 5 * 1024 * 1024:
                errors.append('La imagen es demasiado grande')
            if errors:
                raise serializers.ValidationError(errors)
        return image_obj

##### CATEGORY SERIALIZER

class CategorySerializer(serializers.ModelSerializer):
    """
    Gestiona las categorías de producto. Se asegura que el nombre tenga mínimo
    3 caracteres y no duplique otras categorías existentes.
    """
    name_category =serializers.CharField(
        label = 'Nombre de categoría',
        style = {'placeholder':'Escribe el nombre de la categoría'},
        required = True,
        trim_whitespace = True
    )
    class Meta:
        model = Category
        fields = '__all__'
    def validate_name_category(self, value):
        category_obj = value.upper().strip()
        queryset= Category.objects.filter(name_category__iexact = category_obj)
        errors = []
        letter_count = 0
        if len(category_obj)< 3:
            errors.append('El nombre de la categoría debe tener al menos 3 caracteres')
        for letter in category_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count <3:
            errors.append('El nombre de la categoría debe tener al menos 3 letras')
        if not re.search(r'[a-zA-Z\sñÑ]', category_obj):
            errors.append('El nombre de la categoría contiene caracteres no válidos')
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            errors.append('El nombre de la categoría ya existe')
        if errors:
            raise serializers.ValidationError(errors)
        return category_obj


##### BRAND SERIALIZER

class BrandSerializer(serializers.ModelSerializer):
    """
    Controla las marcas de productos, evitando duplicados y nombres inválidos.
    """
    name_brand = serializers.CharField(
        label = 'Marca',
        style = {'placeholder':'Escribe el nombre de la marca'},
        required = True,
        trim_whitespace = True
    )
    class Meta:
        model = Brand
        fields = '__all__'
    def validate_name_brand(self, value):
        brand_obj = value.upper().strip()
        queryset = Brand.objects.filter(name_brand__iexact = brand_obj)
        errors = []
        letter_count = 0
        if len(brand_obj) < 3:
            errors.append('El nombre de la marca debe contener al menos 3 caracteres')
        for letter in brand_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 2:
            errors.append('El nombre de la marca debe tener al menos 2 letras')
        
        if  re.search (r'[^a-zA-Z0-9\s\-\.\,ñÑ]', brand_obj):
            errors.append('El nombre de la categoría contiene caracteres no válidos')
        if self.instance:
            queryset = queryset.exclude(pk = self.instance.pk)
        if queryset.exists():
            errors.append('El nombre de la marca ya existe')
        if errors:
            raise serializers.ValidationError(errors)
        return brand_obj
##### REGISTER VALORATION

class RegisterValorationSerialize(serializers.ModelSerializer):
    """
    Permite a un usuario registrar una valoración (1-5) para un producto. Cada
    vez que se crea, actualiza la media del producto.
    """
    id = serializers.ReadOnlyField()
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    user_name = serializers.ReadOnlyField(
        source = 'user.username')
    product = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar producto',
        queryset = Products.objects.all()
    ) 
    product_name = serializers.ReadOnlyField(
        source = 'product.name_product'
    )
    valoration = serializers.IntegerField(
        label = 'Valoración',
        default = 1,
    ) 
    class Meta:
        model = Valorations
        fields =['id','user','user_name','product','product_name','valoration']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset = Valorations.objects.all(),
                fields = ['user','product'],
                message='No puedes valorar el mismo producto 2 veces'
            )
        ]
    def validate_valoration(self,value):
        valoration_obj = value
        if valoration_obj is None or valoration_obj < 1:
            valoration_obj = 1
        if valoration_obj > 5:
            valoration_obj=5
        return valoration_obj
    @transaction.atomic
    def create(self, validated_data):
        instance_valoration = super().create(validated_data)
        product_select = validated_data.get('product')
        product_valorations = Valorations.objects.filter(product = product_select).aggregate(total = Avg('valoration'))
        total_avg_valoration = product_valorations.get('total')
        product_select.product_valoration = round(total_avg_valoration,2)
        product_select.save()
        return instance_valoration
        
##### REGISTER COMMENTS SERIALIZER

class RegisterCommentSerializer(serializers.ModelSerializer):
    """
    Maneja los comentarios que los usuarios dejan sobre los productos. Se
    verifica que el usuario que intenta modificar sea el autor del comentario.
    """
    id = serializers.ReadOnlyField()
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    user_name = serializers.ReadOnlyField(source='user.username')
    product = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar producto',
        queryset = Products.objects.all()
    )
    product_name = serializers.ReadOnlyField(
        source = 'product.name_product'
    )
    comment = serializers.CharField(
        label = 'Comentario',
        required= True,
        style = {
            'placeholder':'Escribe tu comentario',
            'style':'resize:none; min-height:2rem;max-height:10rem;'
        }

    )
    class Meta:
        model = Comments
        fields = ['id','user','user_name','product','product_name','comment','date']

    def validate(self, attrs):
        user = self.context.get('request').user
        comment_user = attrs.get('user')
        error = {}
        if user != comment_user:
            error['user']='No tienes permiso para modificar este comentario'
        if error:
            raise serializers.ValidationError(error)
        return attrs