from ..serializers import userserializer
from ..permission import IsStaffUser, IsAnonymousUser
from ..models import UserProfile, Country
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User

####REGISTER STAFF USER VIEWSET
class RegisterStaffUserViewset(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = userserializer.RegisterStaffUserSerializer
    permission_classes = [IsStaffUser]
    queryset = User.objects.all()

####REGISTER USER VIEWSET
class RegisterUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = userserializer.RegisterUserSerializer
    permission_classes = [IsAnonymousUser]
    queryset = User.objects.all()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'Usuario creado':'Registro completado'
            }, status=status.HTTP_200_OK
        )
####PROVINCIE VIEWSET
class RegisterProvincieViewSet(viewsets.ModelViewSet):
    serializer_class = userserializer.RegisterProvincieSerializer
    permission_classes = [IsStaffUser]
    queryset = Country.objects.all()
####USER UPDATE VIEWSET
class UserUpdateViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.action == 'update_user':
            return userserializer.UpdateUserSerializer
        if self.action == 'update_password':
            return userserializer.UpdatePasswordSerializer   
        return userserializer.UpdateProfileUserSerializer
    def get_queryset(self):
        if self.action =='update_user' or self.action =='update_password':
            return User.objects.all()
        return UserProfile.objects.all()
    @action (detail = False, methods = ['get','patch','put'], url_path='update_user')
    def update_user(self, request):
        instance = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        serializer = self.get_serializer(data = request.data, instance = instance, context={'request':request}, partial = True)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
            {
                'exito':'Los datos se modificaron satisfactoriamente'
            }, status=status.HTTP_200_OK
        )
    @action (detail=False, methods = ['post'], url_path='update_password')
    def update_password(self, request):
        instance = request.user
        serializer = self.get_serializer(data = request.data, instance = instance, context = {'request':request})
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
            {
                'exito':'La contraseña se modifico satisfactoriamente'
            }
        )
    @action (detail = False , methods = ['get','patch','put'], url_path='update_profile')
    def update_profile(self, request):
        instance = request.user.profile
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        serializer = self.get_serializer(data = request.data , instance = instance, context = {'request':request}, partial = True)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
            {
                'exito':'El perfil se modifico satisfactoriamente'
            }
        )

    