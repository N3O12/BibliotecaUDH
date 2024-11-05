from rest_framework import serializers
from .models import Usuario, Libro, Genero, Comentario, Favorito, HistorialVisualizacion
from django.contrib.auth.hashers import make_password   
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from .models import Comentario, Libro
import logging
logger = logging.getLogger('api')  

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        return token

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    imagen_perfil_url = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 
            'fecha_registro', 'imagen_perfil', 'imagen_perfil_url'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'imagen_perfil': {'required': False}
        }

    def get_imagen_perfil_url(self, obj):
        if obj.imagen_perfil:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.imagen_perfil.url)
        return None

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        user = Usuario.objects.create_user(
            username=username,
            email=email
        )
        
        if password:
            user.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        
        user.save()
        return user

class LibroSerializer(serializers.ModelSerializer):
    generos = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    portada_url = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = '__all__'

    def create(self, validated_data):
        generos_data = validated_data.pop('generos', [])
        libro = Libro.objects.create(**validated_data)
        for genero_nombre in generos_data:
            genero, _ = Genero.objects.get_or_create(nombre=genero_nombre)
            libro.generos.add(genero)
        return libro

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['generos'] = [genero.nombre for genero in instance.generos.all()]
        return representation

    def validate(self, data):
        required_fields = ['titulo', 'autor', 'isbn', 'descripcion', 'fecha_publicacion']
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(f"El campo '{field}' es requerido.")
        return data

    def get_portada_url(self, obj):
        if obj.portada:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.portada.url)
        return None

    def update(self, instance, validated_data):
        generos_data = validated_data.pop('generos', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if generos_data is not None:
            instance.generos.set(generos_data)
        instance.save()
        return instance
class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

class ComentarioSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    libro = LibroSerializer(read_only=True)  # Añadimos el LibroSerializer completo
    fecha_creacion = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    imagen_perfil_url = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'usuario', 'libro', 'contenido', 'fecha_creacion', 'imagen_perfil_url']
        read_only_fields = ['id', 'usuario', 'libro', 'fecha_creacion', 'imagen_perfil_url']

    def get_imagen_perfil_url(self, obj):
        try:
            request = self.context.get('request')
            
            if not hasattr(obj, 'usuario') or not obj.usuario:
                logger.warning(f"Usuario no encontrado para el comentario {obj.id}")
                return None

            if not hasattr(obj.usuario, 'imagen_perfil') or not obj.usuario.imagen_perfil:
                logger.debug(f"Usuario {obj.usuario} no tiene imagen de perfil")
                return None

            if request:
                return request.build_absolute_uri(obj.usuario.imagen_perfil.url)
            
            return obj.usuario.imagen_perfil.url

        except Exception as e:
            logger.error(f"Error al obtener URL de imagen de perfil: {str(e)}")
            return None

    def to_representation(self, instance):
        try:
            representation = super().to_representation(instance)
            
            # Asegurarnos de que el libro tenga toda la información necesaria
            if instance.libro:
                libro_data = representation.get('libro', {})
                libro_data.update({
                    'titulo': instance.libro.titulo,
                    'autor': instance.libro.autor,
                    'portada_url': self.context.get('request').build_absolute_uri(instance.libro.portada.url) if instance.libro.portada else None,
                    'generos': [genero.nombre for genero in instance.libro.generos.all()]
                })
                representation['libro'] = libro_data
            
            return representation
        except Exception as e:
            logger.error(f"Error al serializar comentario {instance.id}: {str(e)}")
            return {
                'id': instance.id,
                'usuario': str(instance.usuario),
                'libro': {
                    'titulo': instance.libro.titulo if instance.libro else 'Libro no disponible',
                    'autor': instance.libro.autor if instance.libro else '',
                    'portada_url': None
                },
                'contenido': instance.contenido,
                'fecha_creacion': instance.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                'imagen_perfil_url': None
            }

class FavoritoSerializer(serializers.ModelSerializer):
    libro = LibroSerializer(read_only=True)  
    
    class Meta:
        model = Favorito
        fields = ['id', 'libro', 'fecha_agregado']
        read_only_fields = ['fecha_agregado']

    def to_representation(self, instance):
        libro = instance.libro
        return {
            'id': libro.id,  
            'titulo': libro.titulo,
            'autor': libro.autor,
            'portada_url': libro.portada.url if libro.portada else None,
            'generos': [genero.nombre for genero in libro.generos.all()],
            'favorito_id': instance.id  
        }

class HistorialVisualizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialVisualizacion
        fields = '__all__'