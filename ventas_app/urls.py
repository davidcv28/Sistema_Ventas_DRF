from django import urls
from django.urls import path, include
from rest_framework import routers
from .viewsets import userviewset, productviewset, cartviewset
router = routers.DefaultRouter()
####USER ROUTERS####
router.register(f'user_admin', userviewset.RegisterStaffUserViewset, basename='Admin_Users' )
#USER REGISTER
router.register(f'registro', userviewset.RegisterUserViewSet, basename='User_register')
#USER UPDATE
router.register(f'user_update_info', userviewset.UserUpdateViewSet, basename='User_edit')
#REGISTER PROVINCIE
router.register(f'provincia', userviewset.RegisterProvincieViewSet, basename='Admin_Provincie')



####PRODUCTS ROUTERS #####

###REGISTER PRODUCT 
router.register(f'register_product', productviewset.RegisterProductViewSet, basename='Admin_Product')
###REGISTER category 
router.register(f'register_category', productviewset.RegisterCategoryViewSet, basename='Admin_category')
###REGISTER brand 
router.register(f'register_brand', productviewset.RegisterBrandViewSet, basename='Admin_brand')
###REGISTER VALORATION
router.register(f'valoration_product', productviewset.RegisterValorationViewSet, basename='Admin_Valoration')
###REGISTER COMMENT
router.register(f'comment_add', productviewset.RegisterCommentsViewSet, basename='Comment_add')


####CART ROUTERS ####

###REGISTER CART ITEM
router.register(f'add_item_cart', cartviewset.RegisterCartItemViewSet, basename='Add_cart')
###LIST CART
router.register(f'cart_view', cartviewset.ListCartViewSet, basename='Cart_view')


#### INVOICE ROUTERS ####

####REGISTER INVOICE
router.register(f'invoice', cartviewset.RegisterInvoiceViewSet, basename='Invoice')

urlpatterns = [
    path('', include(router.urls))
]
