from rest_framework import viewsets, mixins, response, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..permission import IsStaffUser, IsAnonymousUser, IsOwnerOrReadOnly
from ..serializers import cartserializer
from ..models import Cart, CartItem, Invoice, DetailPurchase

####REGISTER CART ITEM VIEWSET
class RegisterCartItemViewSet(viewsets.ModelViewSet):
    serializer_class = cartserializer.RegisterCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.select_related('cart','product').filter(cart = self.request.user.cart_user)
    
####LIST CART VIEWSET
class ListCartViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = cartserializer.CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Cart.objects.select_related('user').filter(user = self.request.user)

#####INVOICE REGISTER VIEWSET
class RegisterInvoiceViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.action == 'generate_invoice':
            return cartserializer.RegisterInvoiceSerializer
        if self.action == 'invoices':
            return cartserializer.ListInvoiceSerializer
        return cartserializer.ListInvoiceAndDetailSerializer
    def get_queryset(self):
        return Invoice.objects.filter(user = self.request.user).prefetch_related('detail_purchase')
    @action (detail = False, methods = ['post'], url_path='generate_invoice')
    def generate_invoice(self, request):
        serializer = self.get_serializer(request = request.data, context = {'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'exito':'Factura creada'
            }, status=status.HTTP_201_CREATED
        )
    @action (detail=False, methods = ['get'], url_path='invoices')
    def invoices(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(
            serializer.data
        )
    @action (detail=False, methods = ['get'], url_path='invoices_details')
    def invoices_details(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many = True)
        return Response(
            serializer.data
        )
    
   