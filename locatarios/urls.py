from django.urls import path
from . import views

urlpatterns = [
    # Auth locatario
    path('registro/',  views.registro,     name='registro'),
    path('login/',     views.login_view,   name='login'),
    path('recuperar/', views.recuperar_password, name='recuperar_password'),
    path('logout/',    views.logout_view,  name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Productos
    path('productos/agregar/',       views.agregar_producto,  name='agregar_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # Promociones
    path('promociones/agregar/',         views.agregar_promocion,  name='agregar_promocion'),
    path('promociones/editar/<int:pk>/', views.editar_promocion,   name='editar_promocion'),
    path('promociones/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar_promocion'),

    # Trabajadores
    path('trabajadores/agregar/',          views.agregar_trabajador,  name='agregar_trabajador'),
    path('trabajadores/editar/<int:pk>/',  views.editar_trabajador,   name='editar_trabajador'),
    path('trabajadores/eliminar/<int:pk>/', views.eliminar_trabajador, name='eliminar_trabajador'),

    # Fotos (galería MongoDB)
    path('fotos/subir/',                views.subir_foto,     name='subir_foto'),
    path('fotos/eliminar/<str:foto_id>/', views.eliminar_foto, name='eliminar_foto'),

    # Solicitudes de cambio
    path('cambios/solicitar/', views.solicitar_cambio, name='solicitar_cambio'),

    # Panel admin
    path('admin/login/',    views.admin_login,   name='admin_login'),
    path('admin/logout/',   views.admin_logout,  name='admin_logout'),
    path('admin/panel/',    views.admin_panel,   name='admin_panel'),
    path('admin/aprobar/<int:pk>/',          views.admin_aprobar,          name='admin_aprobar'),
    path('admin/rechazar/<int:pk>/',         views.admin_rechazar,         name='admin_rechazar'),
    path('admin/licencia/<int:pk>/',         views.admin_generar_licencia, name='admin_licencia'),
    path('admin/cambio/aprobar/<int:pk>/',   views.admin_aprobar_cambio,   name='admin_aprobar_cambio'),
]
