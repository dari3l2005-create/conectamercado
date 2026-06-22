from django.contrib import admin
from .models import Locatario, Producto, Promocion, SolicitudCambio

admin.site.register(Locatario)
admin.site.register(Producto)
admin.site.register(Promocion)
admin.site.register(SolicitudCambio)
