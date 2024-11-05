from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Usuario(AbstractUser):
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column='UsuarioFechaRegistro')
    imagen_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, db_column='UsuarioImagenPerfil')

    class Meta:
        db_table = 'TB_USUARIO'

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True, db_column='GeneroNombre')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'TB_GENERO'

    @classmethod
    def crear_generos_predefinidos(cls):
        generos = [
            # Ficción General
            'Novela', 'Cuento', 'Poesía', 'Drama', 'Teatro', 'Guion',
        'Literatura contemporánea', 'Literatura clásica', 'Literatura universal',
        'Literatura experimental', 'Literatura epistolar', 'Saga', 'Antología',
        
        # Subgéneros de Ficción
        'Ciencia ficción', 'Fantasía', 'Fantasía épica', 'Fantasía urbana',
        'Fantasía histórica', 'Space Opera', 'Cyberpunk', 'Steampunk',
        'Biopunk', 'Dieselpunk', 'Solarpunk', 'Post-apocalíptico',
        'Distopía', 'Utopía', 'Realismo mágico', 'Surrealismo',
        
        # Thriller y Misterio
        'Thriller', 'Suspense', 'Misterio', 'Noir', 'Neo-noir',
        'Policiaca', 'Espionaje', 'Thriller psicológico',
        'Thriller legal', 'Thriller médico', 'True Crime',
        'Crimen organizado', 'Detective', 'Cozy Mystery',
        
        # Romance y Relaciones
        'Romance', 'Romance histórico', 'Romance contemporáneo',
        'Romance paranormal', 'Romance juvenil', 'Romance erótico',
        'Chick-lit', 'Romance gótico', 'Romance de época',
        'Romance medieval', 'Romance victoriano', 'Romance regencia',
        
        # Terror y Sobrenatural
        'Terror', 'Horror', 'Horror cósmico', 'Horror psicológico',
        'Horror gótico', 'Paranormal', 'Fantasmas', 'Vampiros',
        'Hombres lobo', 'Zombis', 'Ocultismo', 'Supernatural',
        'Lovecraftiano', 'Slasher', 'Body Horror',
        
        # Histórica y Época
        'Histórica', 'Ficción histórica', 'Novela histórica',
        'Antigua Roma', 'Antigua Grecia', 'Medieval', 'Renacimiento',
        'Era Victoriana', 'Belle Époque', 'Años 20s', 'Segunda Guerra Mundial',
        'Guerra Fría', 'Historia alternativa', 'Saga familiar',
        
        # Aventura y Acción
        'Aventura', 'Acción', 'Bélica', 'Western', 'Piratas',
        'Exploración', 'Supervivencia', 'Deportes', 'Artes marciales',
        'Militar', 'Espada y brujería', 'Aventura histórica',
        
        # Literatura Juvenil e Infantil
        'Literatura juvenil', 'Young Adult', 'New Adult',
        'Literatura infantil', 'Cuentos infantiles', 'Fábulas',
        'Libro álbum', 'Middle Grade', 'Coming of age',
        'Literatura juvenil LGBTQ+', 'Fantasía juvenil',
        
        # Humor y Sátira
        'Humor', 'Sátira', 'Parodia', 'Comedia', 'Humor negro',
        'Humor absurdo', 'Sátira política', 'Sátira social',
        
        # No Ficción General
        'Ensayo', 'Biografía', 'Autobiografía', 'Memorias',
        'Crónica', 'Periodismo narrativo', 'Periodismo de investigación',
        'Reportaje', 'Documental', 'Testimonio', 'Historia oral',
        
        # Ciencias Sociales
        'Historia', 'Filosofía', 'Psicología', 'Sociología',
        'Antropología', 'Arqueología', 'Política', 'Economía',
        'Derecho', 'Relaciones internacionales', 'Estudios culturales',
        'Estudios de género', 'Estudios postcoloniales',
        
        # Ciencias y Tecnología
        'Ciencia', 'Divulgación científica', 'Matemáticas',
        'Física', 'Química', 'Biología', 'Astronomía',
        'Cosmología', 'Geología', 'Paleontología', 'Evolución',
        'Neurociencia', 'Inteligencia artificial', 'Robótica',
        'Tecnología', 'Informática', 'Programación', 'Ciberseguridad',
        
        # Medicina y Salud
        'Medicina', 'Anatomía', 'Fisiología', 'Psiquiatría',
        'Nutrición', 'Medicina alternativa', 'Salud mental',
        'Medicina deportiva', 'Farmacología', 'Veterinaria',
        
        # Arte y Cultura
        'Arte', 'Historia del arte', 'Crítica de arte',
        'Música', 'Cine', 'Teatro', 'Danza', 'Fotografía',
        'Arquitectura', 'Diseño', 'Moda', 'Artesanía',
        'Cultura popular', 'Subculturas',
        
        # Desarrollo Personal y Profesional
        'Autoayuda', 'Desarrollo personal', 'Motivación',
        'Liderazgo', 'Gestión del tiempo', 'Productividad',
        'Inteligencia emocional', 'Mindfulness', 'Meditación',
        'Coaching', 'PNL', 'Desarrollo profesional',
        
        # Negocios y Finanzas
        'Negocios', 'Emprendimiento', 'Marketing', 'Ventas',
        'Gestión empresarial', 'Recursos humanos', 'Finanzas',
        'Inversiones', 'Criptomonedas', 'Economía digital',
        'Comercio internacional', 'Startups',
        
        # Estilo de Vida
        'Cocina', 'Gastronomía', 'Vinos', 'Viajes',
        'Guías de viaje', 'Jardinería', 'Decoración',
        'Bricolaje', 'Manualidades', 'Lifestyle',
        'Minimalismo', 'Sostenibilidad',
        
        # Espiritualidad y Religión
        'Espiritualidad', 'Religión', 'Budismo', 'Cristianismo',
        'Islam', 'Judaísmo', 'Hinduismo', 'Taoísmo',
        'Mitología', 'Esoterismo', 'Nueva era', 'Astrología',
        
        # Educación y Academia
        'Educación', 'Pedagogía', 'Didáctica', 'Lingüística',
        'Idiomas', 'Metodología', 'Investigación', 'Tesis',
        'Material didáctico', 'Educación especial',
        
        # Medio Ambiente y Naturaleza
        'Ecología', 'Medio ambiente', 'Cambio climático',
        'Conservación', 'Biodiversidad', 'Sostenibilidad ambiental',
        'Energías renovables', 'Agricultura', 'Permacultura',
        
        # Deportes y Actividad Física
        'Deportes', 'Fitness', 'Yoga', 'Pilates',
        'Entrenamiento personal', 'Nutrición deportiva',
        'Deportes extremos', 'Olimpismo', 'Historia del deporte'
        ]
        for genero in generos:
            cls.objects.get_or_create(nombre=genero)

class Libro(models.Model):
    titulo = models.CharField(max_length=200, db_column='LibroTitulo')
    autor = models.CharField(max_length=100, db_column='LibroAutor')
    isbn = models.CharField(max_length=13, unique=True, db_column='LibroISBN')
    descripcion = models.TextField(db_column='LibroDescripcion')
    fecha_publicacion = models.DateField(db_column='LibroFechaPublicacion')
    portada = models.ImageField(upload_to='libros/portadas/', null=True, blank=True, db_column='LibroPortada')
    url_archivo = models.FileField(upload_to='libros/pdfs/', null=True, blank=True, db_column='LibroArchivo')
    fecha_subida = models.DateTimeField(auto_now_add=True, db_column='LibroFechaSubida')
    generos = models.ManyToManyField(Genero, related_name='libros', db_table='TB_LIBROS_GENEROS')

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'TB_LIBRO'

class Comentario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='ComentarioIdUsuario')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='comentarios', db_column='ComentarioIdLibro')
    contenido = models.TextField(db_column='ComentarioContenido')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='ComentarioFechaCreacion')

    def __str__(self):
        return f'Comentario de {self.usuario.username} en {self.libro.titulo}'
    
    class Meta:
        db_table = 'TB_COMENTARIO'

class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoritos', db_column='FavoritoIdUsuario')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='favoritos', db_column='FavoritoIdLibro')
    fecha_agregado = models.DateTimeField(auto_now_add=True, db_column='FavoritoFechaAgregado')

    class Meta:
        unique_together = ('usuario', 'libro')
        db_table = 'TB_FAVORITO'
        
    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo}"

class HistorialVisualizacion(models.Model):
    TIPO_ACCION = (
        ('LECTURA', 'Lectura'),
        ('DESCARGA', 'Descarga')
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='HistorialIdUsuario')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, db_column='HistorialIdLibro')
    fecha_visualizacion = models.DateTimeField(auto_now_add=True, db_column='HistorialFechaVisualizacion')
    tipo_accion = models.CharField(
        max_length=10, 
        choices=TIPO_ACCION,
        null=True,
        blank=True,
        db_column='HistorialTipoAccion'
    )

    class Meta:
        db_table = 'TB_HISTORIAL_VISUALIZACION'
        ordering = ['-fecha_visualizacion']

    def __str__(self):
        return f"{self.usuario.username} - {self.libro.titulo} - {self.tipo_accion or 'Sin acción'}"