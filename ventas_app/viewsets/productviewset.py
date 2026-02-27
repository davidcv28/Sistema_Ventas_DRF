from rest_framework import viewsets, mixins, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from ..models import Products, Category, Brand, Valorations, Comments
from ..serializers import productserializer
from ..permission import IsStaffUser, IsOwnerOrReadOnly
from ..filters import ProductsFilterSet
####REGISTER CATEGORY VIEWSET
class RegisterCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = productserializer.CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()
####REGISTER Brand VIEWSET
class RegisterBrandViewSet(viewsets.ModelViewSet):
    serializer_class = productserializer.BrandSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Brand.objects.all()
####REGISTER PRODUCT VIEWSET
class RegisterProductViewSet(viewsets.ModelViewSet):
    serializer_class = productserializer.ProductRegisterSerializer
    queryset = Products.objects.select_related('category_product', 'brand_product').all()
    parser_classes = [FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductsFilterSet
    ordering_fields = ['price_product']
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsStaffUser()]
    def create(self, request):
        serializer = self.get_serializer(data = request.data, context = {'request':request})
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
            {
                'Exito':'El producto se registro satisfactoriamente'
            }, status=status.HTTP_201_CREATED
        )

####REGISTER VALORATION VIEWSET
class RegisterValorationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = productserializer.RegisterValorationSerialize
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Valorations.objects.select_related('user','product').all()
        return Valorations.objects.select_related('user','product').filter(user=self.request.user)

####REGISTER COMMENTS VIEWSET
class RegisterCommentsViewSet(viewsets.ModelViewSet):
    serializer_class = productserializer.RegisterCommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset =Comments.objects.select_related('user','product').all()

