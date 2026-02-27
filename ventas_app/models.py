from django.db import models
from django.db.models import aggregates, Aggregate, Sum, Count, F
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils import timezone

#########################################
###############USER MODELS###############
#########################################

class MaritalStatus(models.Model):
    status = models.CharField(max_length=50, unique=True)
class Country(models.Model):
    name_country = models.CharField(max_length=80, unique=True)
    def __str__(self):
        return f'{self.name_country}'
class UserProfile(models.Model):
    TYPE_DOCUMENT = [
        ('DNI', 'DNI'),
        ('CUIT', 'CUIT/CUIL'),
        ('PAS', 'PASAPORTE')
    ]
    MARITAL_STATS = [
        ('SOLTERO','SOLTERO/A'),
        ('CASADO','CASADO/A'),
        ('VIUDO','VIUDO/A')
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    type_document = models.CharField(max_length=4, choices=TYPE_DOCUMENT, default='DNI')
    document = models.CharField( null = False, max_length=20, unique = True, blank = True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=80)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATS, default='SOLTERO/A')

#########################################
###########PRODUCTS MODELS###############
#########################################

class Category(models.Model):
    name_category = models.CharField(max_length=100, blank=False, null=False, unique = True)
    def __str__(self):
        return f'{self.name_category}'
class Brand(models.Model):
    name_brand = models.CharField( max_length=100, null = False, blank = False, unique = True)
    def __str__(self):
        return f'{self.name_brand}'
class Products(models.Model):
    name_product = models.CharField(max_length=80, null=False,blank=False, unique = True)
    category_product = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand_product = models.ForeignKey(Brand, on_delete=models.PROTECT)
    price_product = models.DecimalField(max_digits=12, decimal_places=2, default=1, null = False, blank= False)
    stock_product = models.PositiveBigIntegerField(default = 1, null = False, blank = False)
    image_product = CloudinaryField('image', null=True, blank = True)
    valoration = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f'{self.name_product} (${self.price_product})'
class Valorations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='valorations')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    valoration = models.PositiveBigIntegerField(default = 1, null = False, blank=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['user', 'product'],
                name='ValorationUniqueConstraint'
            )
        ]

class Comments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000, null = False, blank = False)
    date = models.DateField(auto_now_add=True)

#########################################
###############CART MODELS###############
#########################################

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_user')
    created_at = models.DateField(auto_now_add= True)
    def __str__(self):
        return f'Carrito de {self.user.username}'
    @property
    def total_price(self):
        calculate = self.items_cart.all().aggregate(total = Sum(F('product__price_product') * F('quantity')) )
        total_calculate = calculate.get('total') or 0
        return total_calculate
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items_cart')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default = 1, null=False, blank=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['cart', 'product'],
                name='UniqueCartItemConstraint'
            )
        ]
    @property
    def subtotal(self):
        return self.quantity * self.product.price_product

#########################################
##########PURCHASES MODELS###############
#########################################
class Invoice(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoice')
    number_invoice = models.CharField(max_length=20, unique = True, null= True, blank=True)
    user_first_name =models.CharField(max_length=80)
    user_last_name = models.CharField(max_length=80)
    user_document = models.CharField(max_length=100)
    user_provincie=models.CharField(max_length=100)
    user_address = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(default = 0, max_digits=12, decimal_places=2)

class DetailPurchase(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='detail_purchase')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    name_product = models.CharField(max_length=150, null = True, blank = False)
    price= models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default = 0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)