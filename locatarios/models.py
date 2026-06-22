"""
models.py - locatarios
Tablas en MySQL (XAMPP).
Las fotos de perfil, local, productos, promociones y trabajadores se guardan
como archivos en media/. Las fotos extra de galeria del local siguen en MongoDB.
"""

from django.db import models


class Locatario(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente de aprobación'),
        ('activo',     'Activo'),
        ('suspendido', 'Suspendido'),
    ]

    # ── Datos personales (MySQL) ──────────────────────────────────────────────
    nombre_completo = models.CharField(max_length=150)
    correo          = models.EmailField(unique=True)
    telefono        = models.CharField(max_length=15, blank=True)
    contrasena      = models.CharField(max_length=200)      # Se guarda con hash manual

    # ── Datos del puesto ──────────────────────────────────────────────────────
    nombre_negocio  = models.CharField(max_length=100, blank=True)
    puesto          = models.CharField(max_length=50, blank=True)   # Ej. "Pasillo B - 12"
    descripcion     = models.TextField(blank=True)
    ubicacion       = models.CharField(max_length=200, blank=True)  # Texto libre
    fecha_registro  = models.DateField(auto_now_add=True)

    # ── Fotos ─────────────────────────────────────────────────────────────────
    # foto_perfil  = foto PERSONAL del locatario (aparece dentro de su info)
    # foto_local   = foto del PUESTO/LOCAL (la que se ve en la tarjeta pública)
    foto_perfil     = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    foto_local      = models.ImageField(upload_to='locales/',  blank=True, null=True)

    # ── Control administrativo ────────────────────────────────────────────────
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    licencia        = models.CharField(max_length=50, blank=True)   # Generada por admin
    activo          = models.BooleanField(default=False)            # True solo si tiene licencia

    def __str__(self):
        return f"{self.nombre_negocio} ({self.correo})"

    # ── Calificacion promedio (reseñas) ───────────────────────────────────────
    def promedio_estrellas(self):
        reseñas = self.resena_set.all()
        if not reseñas:
            return 0
        return round(sum(r.calificacion for r in reseñas) / len(reseñas), 1)

    def total_resenas(self):
        return self.resena_set.count()


class Producto(models.Model):
    locatario   = models.ForeignKey(Locatario, on_delete=models.CASCADE)
    nombre      = models.CharField(max_length=100)
    precio      = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen      = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Promocion(models.Model):
    locatario   = models.ForeignKey(Locatario, on_delete=models.CASCADE)
    titulo      = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    vigencia    = models.DateField(blank=True, null=True)
    imagen      = models.ImageField(upload_to='promociones/', blank=True, null=True)

    def __str__(self):
        return self.titulo


class Trabajador(models.Model):
    """Empleados que atienden el puesto del locatario."""
    locatario = models.ForeignKey(Locatario, on_delete=models.CASCADE)
    nombre    = models.CharField(max_length=120)
    puesto    = models.CharField(max_length=80, blank=True)   # Rol: cajero, despachador...
    foto      = models.ImageField(upload_to='trabajadores/', blank=True, null=True)
    fecha     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.locatario.nombre_negocio}"


class Resena(models.Model):
    """Reseña/comentario de un cliente sobre un local (estilo Google Maps)."""
    locatario      = models.ForeignKey(Locatario, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=120)
    calificacion   = models.PositiveSmallIntegerField(default=5)   # 1 a 5 estrellas
    comentario     = models.TextField(blank=True)
    fecha          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.nombre_cliente} ({self.calificacion}★) - {self.locatario.nombre_negocio}"

    def rango_estrellas(self):
        """Lista [1..5] para pintar estrellas llenas/vacias en el template."""
        return range(1, 6)


class SolicitudCambio(models.Model):
    """El locatario pide un cambio; el admin lo aprueba."""
    TIPO_CHOICES = [
        ('nombre_negocio', 'Cambio de nombre del negocio'),
        ('puesto',         'Cambio de puesto'),
        ('descripcion',    'Cambio de descripción'),
        ('ubicacion',      'Cambio de ubicación'),
        ('foto_perfil',    'Cambio de foto del locatario'),
        ('foto_local',     'Cambio de foto del local'),
    ]
    locatario   = models.ForeignKey(Locatario, on_delete=models.CASCADE)
    tipo        = models.CharField(max_length=40, choices=TIPO_CHOICES)
    valor_nuevo = models.TextField(blank=True, default='')
    valor_imagen = models.ImageField(upload_to='cambios_pendientes/', blank=True, null=True)
    aprobada    = models.BooleanField(default=False)
    fecha       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.locatario} - {self.tipo}"
