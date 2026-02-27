from rest_framework import serializers
from ..models import Cart, CartItem, Products, Invoice, DetailPurchase
from django.db import transaction


#### REGISTER CART ITEM SERIALIZER

class RegisterCartItemSerializer(serializers.ModelSerializer):
    """
    Serializador para añadir o modificar ítems en el carrito.

    Controla la cantidad (1‑99) y calcula subtotal; se reutiliza en el
    `CartSerializer` para lista de artículos.
    """
    id= serializers.ReadOnlyField()
    product = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar producto',
        queryset = Products.objects.all()
    )
    product_name = serializers.ReadOnlyField(
        source = 'product.name_product'
    )
    product_price = serializers.ReadOnlyField(
        source = 'product.price_product'
    )
    quantity = serializers.IntegerField(
        label = 'Cantidad',
        style = {'placeholder':'Escribe la cantidad'},
        default = 1,
    )
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = CartItem
        fields = ['id','product', 'product_name','product_price','quantity','subtotal']
    def validate_quantity(self, value):
        quantity_obj = value
        if quantity_obj is None or quantity_obj <1:
            quantity_obj = 1
        if quantity_obj > 99:
            quantity_obj = 99
        return quantity_obj
    def create(self, validated_data):
        product_select = validated_data.get('product')
        product_quantity = validated_data.get('quantity')
        user = self.context.get('request').user
        cart_user = Cart.objects.get(user = user)
        instance, created = CartItem.objects.update_or_create(
            cart = cart_user,
            product=product_select,
            defaults={'quantity': product_quantity}
        )
        return instance

#### CART SERIALIZER

class CartSerializer(serializers.ModelSerializer):
    """
    Representa el carrito completo del usuario, incluyendo los ítems
    anidados (`RegisterCartItemSerializer`) y el total calculado.
    """
    id = serializers.ReadOnlyField()
    user_name = serializers.ReadOnlyField(source = 'user.username')
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    cart = RegisterCartItemSerializer(many = True, read_only = True, source='items_cart')
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = Cart
        fields = ['id','user_name','user','cart','total_price','created_at']



#####INVOICE REGISTER SERIALIZER
class RegisterInvoiceSerializer(serializers.ModelSerializer):
    """
    Crea una factura basada en el contenido del carrito del usuario.

    Reduce stock de los productos, genera `DetailPurchase` y vacía el carrito.
    """
    class Meta:
        model = Invoice
        fields = []

    def create(self, validated_data):
        user = self.context.get('request').user
        user_profile = user.profile 
        user_cart = user.cart_user
        
        if user_cart.items_cart.exists():
            with transaction.atomic():
                new_invoice = Invoice.objects.create(
                    user = user,
                    user_first_name = user.first_name,
                    user_last_name = user.last_name,
                    user_document = user_profile.document,
                    user_provincie = user_profile.country,
                    user_address = user_profile.address,
                    total = round(user_cart.total_price, 2)
                )
                
                invoice_details = []
                for item in user_cart.items_cart.all():
                    if item.product.stock_product < item.quantity:
                        raise serializers.ValidationError(f'No hay stock suficiente de {item.product.name_product}')
                    
                    product_item = item.product
                    product_item.stock_product -= item.quantity
                    product_item.save()
                    
                    item_details = DetailPurchase(
                        invoice = new_invoice,
                        product = product_item,
                        name_product = product_item.name_product,
                        price = product_item.price_product,
                        quantity = item.quantity,
                        subtotal = round(item.subtotal, 2) 
                    )
                    invoice_details.append(item_details)
                DetailPurchase.objects.bulk_create(invoice_details)
                user_cart.items_cart.all().delete()
                
            return new_invoice
        
        raise serializers.ValidationError('El carrito está vacío')

class ListInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializador simple para listar facturas existentes .
    """
    class Meta:
        model = Invoice
        fields = '__all__'
class PurchaseDetailSerializer(serializers.ModelSerializer):
    """
    Muestra los detalles (líneas) de una compra/factura.
    """
    class Meta:
        model = DetailPurchase
        fields = '__all__'
class ListInvoiceAndDetailSerializer(serializers.ModelSerializer):
    """
    Combina factura y sus detalles en un solo serializer para vistas anidadas.
    """
    id = serializers.ReadOnlyField()
    user_first_name = serializers.ReadOnlyField()
    user_last_name = serializers.ReadOnlyField()
    user_document = serializers.ReadOnlyField()
    user_provincie = serializers.ReadOnlyField()
    user_address = serializers.ReadOnlyField()
    invoice_details = PurchaseDetailSerializer(many = True, read_only = True, source = 'detail_purchase')
    total = serializers.ReadOnlyField()
    class Meta:
        model = Invoice
        fields = ['id','user_first_name','user_last_name','user_document','user_provincie','user_address','invoice_details','total']


            