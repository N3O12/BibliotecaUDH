from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Asume que tienes una app llamada 'api'
]
if settings.DEBUG:
       import debug_toolbar
       urlpatterns += [
           path('__debug__/', include(debug_toolbar.urls)),
       ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)