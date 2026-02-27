import django_filters, re
from . import models
from django import forms

####PRODUCT FILTERS
class ProductsFilterSet(django_filters.FilterSet):
    name_product = django_filters.CharFilter(
        label = 'Buscar producto',
        field_name= 'name_product',
        lookup_expr='icontains',
        widget = forms.TextInput(attrs={'placeholder':'Buscar producto...'})
    )
    category_product = django_filters.ModelMultipleChoiceFilter(
        label = 'Filtrar por categoria',
        field_name='category_product',
        queryset = models.Category.objects.all(),
        widget= forms.CheckboxSelectMultiple()
    )
    brand_product = django_filters.ModelMultipleChoiceFilter(
        label = 'Filtrar por marca',
        field_name='brand_product',
        queryset=models.Brand.objects.all(),
        widget = forms.CheckboxSelectMultiple()
    )
    min_price_product = django_filters.NumberFilter(
        label = 'Precio minimo',
        field_name='price_product',
        lookup_expr='gte',
        widget = forms.NumberInput(attrs={'placeholder':'Precio minimo'})
    )
    max_price_product = django_filters.NumberFilter(
        label = 'Precio maximo',
        field_name = 'price_product',
        lookup_expr= 'lte',
        widget = forms.NumberInput(attrs={'placeholder':'Precio maximo'})
    )
    class Meta:
        model = models.Products
        fields = ['name_product','category_product','brand_product','min_price_product','max_price_product']