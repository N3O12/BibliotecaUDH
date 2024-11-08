from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, LibroViewSet, GeneroViewSet, 
    ComentarioViewSet, FavoritoViewSet, 
    HistorialVisualizacionViewSet, MyTokenObtainPairView, 
    admin_user_list, serve_pdf, UserProfileView
)
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static
from django.conf import settings
from . import views 
from .views import ComentarioListAPIView, ComentarioDeleteView

# Configuración del router
router = DefaultRouter()
router.register(r'libros', LibroViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'generos', GeneroViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'favoritos', views.FavoritoViewSet, basename='favoritos') 
router.register(r'historial', HistorialVisualizacionViewSet, basename='historial') 

urlpatterns = [
    # Rutas de autenticación
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas de perfil de usuario
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),  # Mantener solo esta ruta para el perfil
    path('admin/users/', admin_user_list, name='admin-user-list'),
    
    # Rutas de libros y géneros
    path('libros/genres/', views.get_genres, name='get_genres'),
    path('libros/<int:pk>/add_comment/', LibroViewSet.as_view({'post': 'add_comment'}), name='libro-add-comment'),
    path('libros/<int:libro_id>/comments/', 
         ComentarioViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='libro-comments'),
    path('comentarios/', ComentarioListAPIView.as_view(), name='comentario-list'),
    path('comentarios/<int:pk>/', ComentarioDeleteView.as_view(), name='comentario-delete'),
    # Rutas de favoritos
    path('favoritos/check/<int:libro_id>/', 
         views.FavoritoViewSet.as_view({'get': 'check_favorite'}), 
         name='favorito-check'),
    path('favoritos/toggle/', 
         views.FavoritoViewSet.as_view({'post': 'toggle'}), 
         name='favorito-toggle'),
    
    # Ruta para servir PDFs
    path('pdf/<str:file_name>', serve_pdf, name='serve_pdf'),
    
    # Incluir rutas del router al final
    path('', include(router.urls)),
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
