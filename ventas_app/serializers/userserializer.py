from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from ..models import Cart, UserProfile, Country
import re

#### REGISTER STAFF USER SERIALIZER ####
class RegisterStaffUserSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de usuarios de staff con validaciones 
    estrictas de nombre, email y complejidad de contraseña.
    """
    id=serializers.ReadOnlyField()
    first_name = serializers.CharField(
        label= 'Nombre',
        style = {'placeholder':'Escribe tu nombre'},
        required = True,
        trim_whitespace = True
    )
    last_name = serializers.CharField(
        label = 'Apellido',
        style = {'placeholder':'Escribe tu apellido'},
        required = True,
        trim_whitespace = True
    )
    email = serializers.EmailField(
        label = 'Correo electronico',
        style = {'placeholder':'Escribe tu correo electronico', 'input_type':'email'},
        required = True,
        trim_whitespace = True
    )
    username = serializers.CharField(
        label = 'Nombre de usuario',
        style = {'placeholder':'Escribe tu nombre de usuario'},
        required = True,
        trim_whitespace = True
    )
    password = serializers.CharField(
        label = 'Contraseña',
        style = {'placeholder':'Escribe tu contraseña', 'input_type':'password'},
        required = True,
        write_only = True
    )
    password2 = serializers.CharField(
        label = 'Confirmar contraseña',
        style = {'placeholder':'Repite tu contraseña'},
        required = True,
        write_only = True
    )
    is_staff = serializers.BooleanField(
        label = 'Usuario administrador'
    )

    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','username','password','password2','is_staff']

    def validate_first_name(self, value):
        # Normaliza a mayúsculas y verifica longitud mínima de 4 caracteres
        name_obj = value.upper().strip()
        errors = []
        letter_count = 0
        if len(name_obj) < 4:
            errors.append('El nombre debe tener al menos 4 caracteres')
        # Regex para permitir solo letras, espacios y eñes
        if re.search(r'[^a-zA-Z\sñÑ]', name_obj):
            errors.append('El nombre contriene caracteres no valido')
        # Cuenta caracteres alfabéticos para asegurar contenido real
        for letter in name_obj:
            if letter.isalpha():
                letter_count +=1
        if letter_count < 4:
            errors.append('El nombre debe contener al menos 4 letras')
        if errors:
            raise serializers.ValidationError(errors)
        return name_obj

    def validate_last_name(self, value):
        # Validación similar al nombre pero con mínimo de 3 caracteres
        last_name_obj = value.upper().strip()
        errors = []
        letter_count = 0
        if len(last_name_obj)< 3:
            errors.append('El apellido debe tener al menos 4 caracteres')
        if re.search(r'[^a-zA-Z\sñÑ]', last_name_obj):
            errors.append('El apellido contiene caracteres no validos')
        for letter in last_name_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El apellido debe tener al menos 3 letras')
        if errors:
            raise serializers.ValidationError(errors)
        return last_name_obj

    def validate_email(self, value):
        # Valida que el email pertenezca a dominios conocidos y sea único
        email_obj = value.strip()
        queryset = User.objects.filter(email__iexact = email_obj)
        allow_domains = ['@gmail.com','@hotmail.com','@outlook.com','@yahoo.com']
        domain_exists = False
        errors = []
        for domain in allow_domains:
            if email_obj.endswith(domain):
                domain_exists = True
        if not domain_exists:
            errors.append('Dominio ingresado no valido')
        # Excluye al propio usuario en caso de estar editando (instance existe)
        if self.instance:
            queryset = queryset.exclude(pk = self.instance.pk)
        if queryset.exists():
            errors.append('El correo ingresado ya esta en uso')
        if errors:
            raise serializers.ValidationError(errors)
        return email_obj

    def validate_username(self, value):
        # Valida longitud y disponibilidad del nombre de usuario
        username_obj = value.strip()
        queryset = User.objects.filter(username__iexact = username_obj)
        errors = []
        if len(username_obj) < 6:
            errors.append('El nombre de usuario debe tener al menos 6 caracteres')
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            errors.append('El nombre de usuario ingresado ya existe')
        if errors:
            raise serializers.ValidationError(errors)
        return username_obj

    def validate_password(self, value):
        # Validación de seguridad: minúsculas, mayúsculas, números y símbolos
        pass_obj = value
        errors = []
        if len(pass_obj)< 8:
            errors.append('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[a-z]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra minuscula')
        if not re.search(r'[A-Z]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra mayuscula')
        if not re.search(r'[0-9]', pass_obj):
            errors.append('La contraseña debe tener al menos un numero')
        if not re.search(r'[^a-zA-Z0-9]', pass_obj):
            errors.append('La contraseña debe tener al menos un caracter especial')
        if errors:
            raise serializers.ValidationError(errors)
        return pass_obj

    def validate(self, attrs):
        # Comprobación de que ambas contraseñas ingresadas coincidan
        password1 = attrs.get('password')
        password2 = attrs.get('password2')
        errors ={}
        if password1!= password2:
            errors['password2'] = 'Las contraseñas no coinciden'
        if errors:
            raise serializers.ValidationError(errors)
        # Eliminamos password2 para que no llegue al método create del modelo User
        attrs.pop('password2')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Crea el usuario y su carrito de forma atómica para evitar datos huérfanos
        user = User.objects.create_user(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password'],
            is_staff = validated_data.get('is_staff', False)
        )
        Cart.objects.create(user = user)
        return user

#### REGISTER USER SERIALIZER ####
class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de clientes finales con creación 
    automática de Perfil y Carrito.
    """
    id = serializers.ReadOnlyField()
    first_name = serializers.CharField(
        label = 'Nombre',
        style = {'placeholder':'Escribe tu nombre'},
        required = True,
        trim_whitespace = True,
        write_only = True
    )
    last_name = serializers.CharField(
        label = 'Apellido',
        style = {'placeholder':'Escribe tu apellido'},
        required = True,
        trim_whitespace = True,
        write_only = True
    )
    email = serializers.EmailField(
        label = 'Correo electronico',
        style = {'placeholder':'Escribe tu correo'},
        required = True,
        trim_whitespace = True,
        write_only = True
    )
    username = serializers.CharField(
        label = 'Nombre de usuarios',
        style = {'placeholder':'Escribe tu nombre de usuario'},
        required = True,
        trim_whitespace = True,
        write_only = True
    )
    password = serializers.CharField(
        label = 'Contraseña',
        style = {'placeholder':'Escribe tu contraseña', 'help_text':'La contraseña debe contener 8 caracteres, 1 mayuscula, 1 minuscula, 1 caracter especial y 1 numero', 'input_type':'password'},
        required = True,
        write_only = True
    )
    password2 = serializers.CharField(
        label = 'Confirmar contraseña',
        style = {'placeholder':'Repetir contraseña', 'input_type':'password'},
        required = True,
        write_only = True
    )
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name','email','username','password','password2']

    def validate_first_name(self, value):
        name_obj = value.upper().strip()
        letter_count = 0
        errors = []
        if len(name_obj)< 3:
            errors.append('El nombre debe tener al menos 3 caracteres')
        for letter in name_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El nombre debe tener al menos 3 letras')
        if re.search(r'[^a-zA-Z\sñÑ]', name_obj):
            errors.append('El nombre contiene caracteres no validos')
        if errors:
            raise serializers.ValidationError(errors)
        return name_obj

    def validate_last_name(self, value):
        lastname_obj = value.upper().strip()
        letter_count = 0
        errors = []
        if len(lastname_obj)< 3:
            errors.append('El apellido debe tener al menos 3 caracteres')
        if re.search(r'[^a-zA-Z\sñÑ]', lastname_obj):
            errors.append('El apellido contiene caracteres no validos')
        for letter in lastname_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El apellido debe tener al menos 3 letras')
        if errors:
            raise serializers.ValidationError(errors)
        return lastname_obj

    def validate_email(self, value):
        email_obj = value.strip()
        queryset = User.objects.filter(email__iexact = email_obj)
        allow_domains = ['@gmail.com','@hotmail.com', '@outlook.com','@yahoo.com']
        domain_exist = False
        errors =[]
        for domain in allow_domains:
            if email_obj.endswith(domain):
                domain_exist = True
        if not domain_exist:
            errors.append('Dominio ingresado no valido')
        if queryset.exists():
            errors.append('El correo ingresado ya esta en uso')
        if errors:
            raise serializers.ValidationError(errors)
        return email_obj

    def validate_username(self, value):
        username_obj = value.strip()
        queryset = User.objects.filter(username__iexact = username_obj)
        errors = []
        if len(username_obj)< 6:
            errors.append('El nombre de usuario debe tener al menos 6 caracteres')
        if queryset.exists():
            errors.append('EL nombre de usuario ingresado ya esta en uso')
        if errors:
            raise serializers.ValidationError(errors)
        return username_obj

    def validate_password(self, value):
        pass_obj = value
        errors = []
        if len(pass_obj)< 8:
            errors.append('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[a-zñ]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra minuscula')
        if not re.search(r'[A-ZÑ]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra mayuscula')
        if not re.search(r'[0-9]', pass_obj):
            errors.append('La contraseña debe tener al menos un numero')
        if not re.search(r'[^a-zA-Z0-9ñÑ]', pass_obj):
            errors.append('La contraseña debe tener al menos un caracter especial')
        if errors:
            raise serializers.ValidationError(errors)
        return pass_obj

    def validate(self, attrs):
        password1 = attrs.get('password')
        password2 = attrs.get('password2')
        errors = {}
        if password1 != password2:
            errors['password2']='Las contraseñas no coinciden'
        if errors:
            raise serializers.ValidationError(errors)
        attrs.pop('password2')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Creamos el usuario base y vinculamos Carrito y Perfil adicionales
        user = User.objects.create_user(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email= validated_data['email'],
            username = validated_data['username'],
            password= validated_data['password']
        )
        Cart.objects.create(user = user)
        UserProfile.objects.create(user = user)
        return user

#### UPDATE USER SERIALIZER ####
class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Permite actualizar los datos básicos del usuario (Nombre, Apellido, Email).
    Mantiene el ID y el Username como campos de solo lectura por seguridad.
    """
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.CharField(
        label = 'Nombre',
        style = {'placeholder':'Escribe tu nombre'},
        required = True,
        trim_whitespace = True,
    )
    last_name = serializers.CharField(
        label = 'Apellido',
        style = {'placeholder':'Escribe tu apellido'},
        required = True,
        trim_whitespace = True,
    )
    email = serializers.EmailField(
        label = 'Correo electronico',
        style = {'placeholder':'Escribe tu correo'},
        required = True,
        trim_whitespace = True,
    )
    class Meta:
        model = User
        fields = ['id','username','first_name', 'last_name', 'email']

    def validate_first_name(self, value):
        name_obj = value.upper().strip()
        letter_count = 0
        errors = []
        if len(name_obj)< 3:
            errors.append('El nombre debe tener al menos 3 caracteres')
        for letter in name_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El nombre debe tener al menos 3 letras')
        if re.search(r'[^a-zA-Z\sñÑ]', name_obj):
            errors.append('El nombre contiene caracteres no validos')
        if errors:
            raise serializers.ValidationError(errors)
        return name_obj

    def validate_last_name(self, value):
        lastname_obj = value.upper().strip()
        letter_count = 0
        errors = []
        if len(lastname_obj)< 3:
            errors.append('El apellido debe tener al menos 3 caracteres')
        if re.search(r'[^a-zA-Z\sñÑ]', lastname_obj):
            errors.append('El apellido contiene caracteres no validos')
        for letter in lastname_obj:
            if letter.isalpha():
                letter_count += 1
        if letter_count < 3:
            errors.append('El apellido debe tener al menos 3 letras')
        if errors:
            raise serializers.ValidationError(errors)
        return lastname_obj

    def validate_email(self, value):
        email_obj = value.strip()
        queryset = User.objects.filter(email__iexact = email_obj)
        allow_domains = ['@gmail.com','@hotmail.com', '@outlook.com','@yahoo.com']
        domain_exist = False
        errors =[]
        for domain in allow_domains:
            if email_obj.endswith(domain):
                domain_exist = True
        if not domain_exist:
            errors.append('Dominio ingresado no valido')
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            errors.append('El correo ingresado ya esta en uso')
        if errors:
            raise serializers.ValidationError(errors)
        return email_obj

#### UPDATE PASSWORD SERIALIZER ####
class UpdatePasswordSerializer(serializers.Serializer):
    """
    Serializer dedicado exclusivamente al cambio de contraseña,
    verificando la contraseña actual contra la almacenada.
    """
    old_password = serializers.CharField(
        label ='Contraseña actual',
        style = {'placeholder':'Escribe tu contraseña actual','input_type':'password'},
        required = True,
        write_only = True
    )
    new_password = serializers.CharField(
        label ='Nueva actual',
        style = {'placeholder':'Escribe tu nueva contraseña','input_type':'password'},
        required = True,
        write_only = True
    )
    confirm_password = serializers.CharField(
        label ='Confirmar contraseña',
        style = {'placeholder':'Repite la nueva contraseña','input_type':'password'},
        required = True,
        write_only = True
    )

    def validate_new_password(self,value):
        pass_obj = value
        errors = []
        if len(pass_obj)< 8:
            errors.append('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[a-zñ]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra minuscula')
        if not re.search(r'[A-ZÑ]', pass_obj):
            errors.append('La contraseña debe tener al menos una letra mayuscula')
        if not re.search(r'[0-9]', pass_obj):
            errors.append('La contraseña debe tener al menos un numero')
        if not re.search(r'[^a-zA-Z0-9ñÑ]', pass_obj):
            errors.append('La contraseña debe tener al menos un caracter especial')
        if errors:
            raise serializers.ValidationError(errors)
        return pass_obj

    def validate(self, attrs):
        # Accedemos al usuario desde el contexto de la petición
        user = self.context.get('request').user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        errors ={}
        # Verificamos la contraseña anterior con el método check_password de Django
        if not user.check_password(old_password):
            errors['old_password'] = 'La contraseña actual es incorrecta'
        if new_password == old_password:
            errors['new_password'] = 'La contraseña ingresada no puede ser la que ya tienes'
        if new_password != confirm_password:
            errors['confirm_password'] = 'Las contraseñas no coinciden'
        if errors:
            raise serializers.ValidationError(errors)
        attrs.pop('old_password')
        attrs.pop('confirm_password')
        return attrs

    def update(self, instance,validated_data):
        # Usamos set_password para hashear la contraseña correctamente antes de guardar
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance

#### UPDATE PROFILE USER SERIALIZER ####
class UpdateProfileUserSerializer(serializers.ModelSerializer):
    """
    Actualiza la información del perfil del usuario, incluyendo validación 
    de documentos oficiales (DNI, CUIT, Pasaporte).
    """
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    type_document = serializers.ChoiceField(
        label = 'Tipo de documento',
        choices=UserProfile.TYPE_DOCUMENT)
    document = serializers.CharField(
        label = 'Identificación',
        style = {'placeholder':'Escriba su identificación'},
        trim_whitespace = True
    )
    country = serializers.PrimaryKeyRelatedField(
        label = 'Seleccionar provincia',
        queryset = Country.objects.all()
    )
    address = serializers.CharField(
        label = 'Domicilio',
        style = {'placeholder':'Escribe tu domicilio'},
        trim_whitespace = True
    )
    marital_status = serializers.ChoiceField(
        label = 'Estado civil',
        choices=UserProfile.MARITAL_STATS
    )
    class Meta:
        model = UserProfile
        fields = ['user', 'type_document','document','country','address','marital_status']

    def validate_document(self, value):
        # Lógica compleja para validar formatos de documentos según el país (Argentina)
        document_obj = value.upper()
        type_document = self.initial_data.get('type_document')
        queryset = UserProfile.objects.filter(document__iexact = document_obj)
        errors = []
        if self.instance:
            queryset = queryset.exclude(pk = self.instance.pk)
        if queryset.exists():
            errors.append('La identificación ingresada ya se encuentra registrada')
        
        if type_document:
            # Validación de DNI (7 u 8 dígitos numéricos)
            if type_document == 'DNI':
                if len(document_obj) < 7 or len(document_obj)>8:
                    errors.append('Numero de DNI no valido')
                if re.search(r'[^0-9]', document_obj):
                    errors.append('El dni contiene caracteres no validos')
            # Validación de CUIT/CUIL con prefijos permitidos en Argentina
            if type_document == 'CUIT':
                valid_num = ['20', '23', '24', '27', '30', '33', '34']
                valid_cuit = False
                if len(document_obj) != 11:
                    errors.append('Numero de CUIT/CUIL no valido')
                for valid in valid_num:
                    if  document_obj.startswith(valid):
                        valid_cuit = True
                        break
                if not valid_cuit:
                    errors.append('Prefijo CUIT/CUIL no valido')
            # Validación de Pasaporte (alfanumérico)
            if type_document == 'PAS':
                if len(document_obj)< 6 or len(document_obj)>20:
                    errors.append('Identificación de pasaporte no valido')
                if re.search(r'[^a-zA-Z0-9]', document_obj):
                    errors.append('El codigo del pasaporte contiene caracteres no validos')
            if errors:
                raise serializers.ValidationError(errors)
        return document_obj
    
#### PROVINCIE SERIALIZER ####
class RegisterProvincieSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar provincias, asegurando que 
    el nombre coincida con las provincias reales de Argentina.
    """
    id = serializers.ReadOnlyField()
    name_country = serializers.CharField(
        label = 'Provincia',
        style = {'placeholder':'Escribe el nombre de tu provincia'},
        required = True,
        trim_whitespace = True
    )
    class Meta:
        model = Country
        fields = ['id','name_country']

    def validate_name_country(self, value):
        # Verifica que la provincia ingresada esté en el listado oficial y no esté duplicada
        provinces_obj = value.upper().strip()
        queryset = Country.objects.filter(name_country__iexact = provinces_obj)
        provinces_argentina = [
            "BUENOS AIRES", "CIUDAD AUTONOMA DE BUENOS AIRES", "CATAMARCA", "CHACO",
            "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY",
            "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO",
            "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE",
            "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"
        ]
        errors = []
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            errors.append('El nombre de la pronvicia ingresada ya existe')
        if provinces_obj not in provinces_argentina:
            errors.append('La provincia ingresada no existe en argentina')
        if errors:
            raise serializers.ValidationError(errors)
        return provinces_obj
