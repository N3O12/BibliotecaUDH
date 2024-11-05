from django.contrib.auth import authenticate
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import os
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser as DRFIsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import Usuario, Libro, Genero, Comentario, Favorito, HistorialVisualizacion
from .serializers import (
    UsuarioSerializer, LibroSerializer, GeneroSerializer, 
    ComentarioSerializer, FavoritoSerializer, HistorialVisualizacionSerializer, 
    MyTokenObtainPairSerializer
)
from .permissions import IsAdminUser, IsNormalUser
import logging
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.datastructures import MultiValueDict
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Libro, Comentario
from .serializers import LibroSerializer, ComentarioSerializer
from rest_framework.decorators import action, api_view, parser_classes
from rest_framework.parsers import JSONParser
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from .models import Genero
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Favorito, Libro
from .serializers import FavoritoSerializer
def get_genres(request):
       genres = list(Genero.objects.values_list('nombre', flat=True))
       print("Géneros obtenidos:", genres)  # Añade esta línea para depuración
       return JsonResponse(genres, safe=False)

from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io 
import os
from rest_framework import generics
class ComentarioListAPIView(generics.ListAPIView):
    queryset = Comentario.objects.all().order_by('-fecha_creacion')
    serializer_class = ComentarioSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ComentarioDeleteView(generics.DestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Comentario eliminado exitosamente"},
                status=status.HTTP_200_OK
            )
        except Comentario.DoesNotExist:
            return Response(
                {"error": "Comentario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def validate_image(self, image_file):
        try:
            img = Image.open(image_file)
            img.verify()
            image_file.seek(0)
            return True, None
        except Exception as e:
            return False, str(e)

    def put(self, request):
        try:
            user = request.user
            logger.info(f"Actualizando perfil para usuario: {user.username}")

            if 'imagen_perfil' in request.FILES:
                imagen = request.FILES['imagen_perfil']
                
                # Validar imagen
                is_valid, error = self.validate_image(imagen)
                if not is_valid:
                    return Response(
                        {'error': f'Imagen inválida: {error}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Eliminar imagen anterior
                if user.imagen_perfil:
                    try:
                        if os.path.isfile(user.imagen_perfil.path):
                            os.remove(user.imagen_perfil.path)
                    except Exception as e:
                        logger.error(f"Error eliminando imagen anterior: {e}")

                # Procesar y guardar nueva imagen
                try:
                    # Asegurar extensión válida
                    ext = os.path.splitext(imagen.name)[1].lower()
                    if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                        ext = '.jpg'
                    
                    new_filename = f"perfil_{user.username}_{os.urandom(8).hex()}{ext}"
                    file_path = f'perfiles/{new_filename}'

                    # Optimizar imagen
                    img = Image.open(imagen)
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, 'white')
                        background.paste(img, mask=img.split()[-1])
                        img = background

                    # Redimensionar si es necesario
                    max_size = (800, 800)
                    img.thumbnail(max_size, Image.LANCZOS)

                    # Guardar imagen optimizada
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)

                    saved_path = default_storage.save(file_path, ContentFile(buffer.read()))
                    user.imagen_perfil = saved_path
                    user.save()
                    
                except Exception as e:
                    logger.error(f"Error procesando imagen: {e}")
                    return Response(
                        {'error': 'Error al procesar la imagen'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = UsuarioSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            logger.error(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return Response(
                {'error': 'Error al actualizar el perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def get(self, request):
        try:
            serializer = UsuarioSerializer(request.user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error en get profile: {str(e)}")
            return Response(
                {'error': 'Error al obtener el perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        try:
            serializer = UsuarioSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error en update profile: {str(e)}")
            return Response(
                {'error': 'Error al actualizar el perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@xframe_options_exempt
def serve_pdf(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'libros', 'pdfs', file_name)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response
    else:
        return HttpResponse('El archivo no existe', status=404)

@api_view(['GET'])
@permission_classes([DRFIsAdminUser])
def admin_user_list(request):
    try:
        logger.info(f"Usuario {request.user.username} solicitando lista de usuarios")
        users = Usuario.objects.all().values('id', 'username', 'email')
        logger.info(f"Encontrados {len(users)} usuarios")
        return Response(list(users))
    except Exception as e:
        logger.error(f"Error en admin_user_list: {str(e)}")
        return Response(
            {'error': 'Error al obtener la lista de usuarios'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        logger.info(f"Recibida solicitud para agregar comentario al libro {pk}")
        logger.info(f"Datos recibidos: {request.data}")
        libro = self.get_object()
        
        try:
            serializer = ComentarioSerializer(
                data=request.data,
                context=self.get_serializer_context()  # Usar el método existente
            )
        
            if serializer.is_valid():
                comentario = serializer.save(usuario=request.user, libro=libro)
                return Response(
                    ComentarioSerializer(
                        comentario, 
                        context=self.get_serializer_context()
                    ).data,
                    status=status.HTTP_201_CREATED
                )
            
            logger.error(f"Error al agregar comentario: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error inesperado al agregar comentario: {str(e)}")
            return Response(
                {"detail": "Se produjo un error al procesar el comentario"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        libro = self.get_object()
        comentarios = Comentario.objects.filter(libro=libro).order_by('-fecha_creacion')
        serializer = ComentarioSerializer(
            comentarios, 
            many=True, 
            context=self.get_serializer_context()
        )
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        logger.info(f"Datos recibidos para actualización: {request.data}")
    
        mutable_data = request.data.copy()
    
        # Manejo de la portada
        if 'portada' in request.FILES:
            portada = request.FILES['portada']
            if instance.portada:
                if os.path.isfile(instance.portada.path):
                    os.remove(instance.portada.path)
            filename = default_storage.save(f'libros/portadas/{portada.name}', ContentFile(portada.read()))
            mutable_data['portada'] = filename
        else:
            mutable_data.pop('portada', None)
    
        # Manejo del archivo PDF
        if 'url_archivo' in request.FILES:
            pdf = request.FILES['url_archivo']
            if instance.url_archivo:
                if os.path.isfile(instance.url_archivo.path):
                    os.remove(instance.url_archivo.path)
            filename = default_storage.save(f'libros/pdfs/{pdf.name}', ContentFile(pdf.read()))
            mutable_data['url_archivo'] = filename
        else:
            mutable_data.pop('url_archivo', None)
    
        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except serializers.ValidationError as e:
            logger.error(f"Error de validación: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return Response({"detail": "Error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        logger.info(f"Datos validados para actualización: {serializer.validated_data}")
        serializer.save()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        print("Datos recibidos en create:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Errores de validación:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
        # Manejo de la portada
        if 'portada' in request.FILES:
            portada = request.FILES['portada']
            filename = default_storage.save(f'libros/portadas/{portada.name}', ContentFile(portada.read()))
            serializer.validated_data['portada'] = filename
        else:
            print("No se recibió archivo de portada")
        # Manejo del archivo PDF
        if 'url_archivo' in request.FILES:
            pdf = request.FILES['url_archivo']
            filename = default_storage.save(f'libros/pdfs/{pdf.name}', ContentFile(pdf.read()))
            serializer.validated_data['url_archivo'] = filename

        # Manejo de los géneros
        generos = request.data.getlist('generos')
        print("Géneros recibidos:", generos)  # Para depuración

        libro = serializer.save()
        for genero_nombre in generos:
            genero, created = Genero.objects.get_or_create(nombre=genero_nombre)
            libro.generos.add(genero)
            print(f"Género {'creado' if created else 'existente'} y añadido: {genero_nombre}")  # Para depuración

        libro.refresh_from_db()  # Actualiza el objeto libro desde la base de datos
        print("Géneros del libro después de guardar:", libro.generos.all())  # Para depuración

        if libro.portada:
            libro.portada_url = request.build_absolute_uri(libro.portada.url)
            libro.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    


class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        libro_id = self.kwargs.get('libro_id')
        return Comentario.objects.filter(libro_id=libro_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        libro_id = self.kwargs.get('libro_id')
        libro = get_object_or_404(Libro, id=libro_id)
        serializer.save(usuario=self.request.user, libro=libro)

class FavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='check/(?P<libro_id>[^/.]+)')
    def check_favorite(self, request, libro_id=None):
        """
        Verifica si un libro está en favoritos
        """
        try:
            is_favorite = Favorito.objects.filter(
                usuario=request.user,
                libro_id=libro_id
            ).exists()
            return Response({'isFavorite': is_favorite})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        libro_id = request.data.get('libro_id')
        if not libro_id:
            return Response({'error': 'Libro ID es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            libro = Libro.objects.get(id=libro_id)
            favorito = Favorito.objects.filter(usuario=request.user, libro=libro)
            
            if favorito.exists():
                favorito.delete()
                return Response({'status': 'removed'})
            else:
                Favorito.objects.create(usuario=request.user, libro=libro)
                return Response({'status': 'added'})
                
        except Libro.DoesNotExist:
            return Response({'error': 'Libro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class HistorialVisualizacionViewSet(viewsets.ModelViewSet):
    serializer_class = HistorialVisualizacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HistorialVisualizacion.objects.filter(
            usuario=self.request.user,
            tipo_accion__isnull=False  # Solo obtener registros con acciones específicas
        )

    @action(detail=False, methods=['post'])
    def registrar_accion(self, request):
        libro_id = request.data.get('libro_id')
        tipo_accion = request.data.get('tipo_accion')
        
        if not libro_id:
            return Response(
                {'error': 'Se requiere libro_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si no hay tipo_accion, no registramos nada
        if not tipo_accion:
            return Response({'message': 'No se registró ninguna acción'})

        # Validar que sea una acción válida
        if tipo_accion not in ['LECTURA', 'DESCARGA']:
            return Response(
                {'error': 'Tipo de acción no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            libro = Libro.objects.get(id=libro_id)
            HistorialVisualizacion.objects.create(
                usuario=request.user,
                libro=libro,
                tipo_accion=tipo_accion
            )
            return Response({
                'status': 'success',
                'message': f'Acción de {tipo_accion.lower()} registrada correctamente'
            })
        except Libro.DoesNotExist:
            return Response(
                {'error': 'Libro no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def estadisticas_libro(self, request):
        """
        Obtener estadísticas de lecturas y descargas de un libro
        """
        libro_id = request.query_params.get('libro_id')
        if not libro_id:
            return Response(
                {'error': 'Se requiere libro_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            libro = Libro.objects.get(id=libro_id)
            lecturas = HistorialVisualizacion.objects.filter(
                libro=libro, 
                tipo_accion='LECTURA'
            ).count()
            descargas = HistorialVisualizacion.objects.filter(
                libro=libro, 
                tipo_accion='DESCARGA'
            ).count()

            return Response({
                'libro': libro.titulo,
                'total_lecturas': lecturas,
                'total_descargas': descargas
            })
        except Libro.DoesNotExist:
            return Response(
                {'error': 'Libro no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({'message': 'Login exitoso'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)