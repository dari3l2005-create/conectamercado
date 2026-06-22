"""
views.py - locatarios
Contiene: registro, login, recuperar contraseña, logout, dashboard,
CRUD de productos/promociones/trabajadores, solicitudes de cambio (incluye fotos)
y panel de admin con aprobaciones y generación de licencia.
"""

import uuid
import base64
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Locatario, Producto, Promocion, Trabajador, Resena, SolicitudCambio
)
from db_mongo import fotos_puestos, fotos_locatario


# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def hash_pass(raw):
    return hashlib.sha256(raw.encode()).hexdigest()

def get_loc_session(request):
    """Devuelve el Locatario activo en sesión, o None."""
    lid = request.session.get('locatario_id')
    if lid:
        try:
            return Locatario.objects.get(pk=lid)
        except Locatario.DoesNotExist:
            pass
    return None


# ─── REGISTRO ─────────────────────────────────────────────────────────────────

def registro(request):
    if request.method == 'POST':
        nombre     = request.POST.get('nombre_completo', '').strip()
        correo     = request.POST.get('correo', '').strip()
        telefono   = request.POST.get('telefono', '').strip()
        pwd        = request.POST.get('contrasena', '')
        foto_loc   = request.FILES.get('foto_perfil')   # foto PERSONAL del locatario
        foto_local = request.FILES.get('foto_local')    # foto del PUESTO/LOCAL

        if Locatario.objects.filter(correo=correo).exists():
            messages.error(request, 'Ese correo ya está registrado.')
            return redirect('registro')

        # Ambas fotos son OBLIGATORIAS para registrarse
        if not foto_loc or not foto_local:
            messages.error(request, 'Debes subir la foto del locatario y la foto del local para registrarte.')
            return redirect('registro')

        loc = Locatario.objects.create(
            nombre_completo=nombre,
            correo=correo,
            telefono=telefono,
            contrasena=hash_pass(pwd),
            estado='pendiente',
            activo=False,
            foto_perfil=foto_loc,
            foto_local=foto_local,
        )

        # Guardar referencia de la foto personal en MongoDB (como antes)
        try:
            fotos_locatario.insert_one({
                'locatario_id': loc.pk,
                'nombre': nombre,
                'archivo': foto_loc.name,
            })
        except Exception:
            pass  # Si MongoDB no está disponible, el registro no se rompe

        messages.success(request, 'Solicitud enviada. El administrador la revisará pronto.')
        return redirect('login')

    return render(request, 'locatarios/registro.html')


# ─── LOGIN ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        pwd    = request.POST.get('contrasena', '')

        try:
            loc = Locatario.objects.get(correo=correo, contrasena=hash_pass(pwd))
        except Locatario.DoesNotExist:
            messages.error(request, 'Credenciales incorrectas.')
            return redirect('login')

        if loc.estado == 'pendiente':
            messages.warning(request, 'Tu solicitud aún está pendiente de aprobación.')
            return redirect('login')

        if loc.estado == 'suspendido':
            messages.error(request, 'Tu cuenta ha sido suspendida. Contacta al administrador.')
            return redirect('login')

        request.session['locatario_id'] = loc.pk
        return redirect('dashboard')

    return render(request, 'locatarios/login.html')


# ─── RECUPERAR CONTRASEÑA ─────────────────────────────────────────────────────
# Flujo simple sin servidor de correo: se verifica con correo + teléfono
# registrados y luego se permite establecer una nueva contraseña.

def recuperar_password(request):
    if request.method == 'POST':
        correo   = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        nueva    = request.POST.get('nueva_contrasena', '')
        confirma = request.POST.get('confirmar_contrasena', '')

        try:
            loc = Locatario.objects.get(correo=correo)
        except Locatario.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo.')
            return redirect('recuperar_password')

        # Verificación de identidad: el teléfono debe coincidir
        if (loc.telefono or '').strip() != telefono or not telefono:
            messages.error(request, 'El teléfono no coincide con el de la cuenta.')
            return redirect('recuperar_password')

        if len(nueva) < 6:
            messages.error(request, 'La nueva contraseña debe tener al menos 6 caracteres.')
            return redirect('recuperar_password')

        if nueva != confirma:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('recuperar_password')

        loc.contrasena = hash_pass(nueva)
        loc.save()
        messages.success(request, 'Contraseña actualizada. Ya puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'locatarios/recuperar.html')


# ─── LOGOUT ───────────────────────────────────────────────────────────────────

def logout_view(request):
    request.session.flush()
    return redirect('index')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def dashboard(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')

    productos    = Producto.objects.filter(locatario=loc)
    promociones  = Promocion.objects.filter(locatario=loc)
    trabajadores = Trabajador.objects.filter(locatario=loc)
    resenas      = Resena.objects.filter(locatario=loc)

    # Fotos del puesto desde MongoDB — convertir _id a string para el template
    fotos = []
    try:
        fotos_raw = list(fotos_puestos.find({'locatario_id': loc.pk}))
        for f in fotos_raw:
            f['foto_id'] = str(f['_id'])
            fotos.append(f)
    except Exception:
        pass

    return render(request, 'locatarios/dashboard.html', {
        'loc': loc,
        'productos': productos,
        'promociones': promociones,
        'trabajadores': trabajadores,
        'resenas': resenas,
        'fotos': fotos,
    })


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

def agregar_producto(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    if request.method == 'POST':
        Producto.objects.create(
            locatario=loc,
            nombre=request.POST.get('nombre', ''),
            precio=request.POST.get('precio', 0),
            descripcion=request.POST.get('descripcion', ''),
            imagen=request.FILES.get('imagen'),
        )
        messages.success(request, 'Producto agregado.')
    return redirect('dashboard')


def editar_producto(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    prod = get_object_or_404(Producto, pk=pk, locatario=loc)
    if request.method == 'POST':
        prod.nombre      = request.POST.get('nombre', prod.nombre)
        prod.precio      = request.POST.get('precio', prod.precio)
        prod.descripcion = request.POST.get('descripcion', prod.descripcion)
        if request.FILES.get('imagen'):
            prod.imagen = request.FILES.get('imagen')
        prod.save()
        messages.success(request, 'Producto actualizado.')
    return redirect('dashboard')


def eliminar_producto(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    get_object_or_404(Producto, pk=pk, locatario=loc).delete()
    messages.success(request, 'Producto eliminado.')
    return redirect('dashboard')


# ─── PROMOCIONES ──────────────────────────────────────────────────────────────

def agregar_promocion(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    if request.method == 'POST':
        Promocion.objects.create(
            locatario=loc,
            titulo=request.POST.get('titulo', ''),
            descripcion=request.POST.get('descripcion', ''),
            vigencia=request.POST.get('vigencia') or None,
            imagen=request.FILES.get('imagen'),
        )
        messages.success(request, 'Promoción agregada.')
    return redirect('dashboard')


def editar_promocion(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    promo = get_object_or_404(Promocion, pk=pk, locatario=loc)
    if request.method == 'POST':
        promo.titulo      = request.POST.get('titulo', promo.titulo)
        promo.descripcion = request.POST.get('descripcion', promo.descripcion)
        promo.vigencia    = request.POST.get('vigencia') or None
        if request.FILES.get('imagen'):
            promo.imagen = request.FILES.get('imagen')
        promo.save()
        messages.success(request, 'Promoción actualizada.')
    return redirect('dashboard')


def eliminar_promocion(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    get_object_or_404(Promocion, pk=pk, locatario=loc).delete()
    messages.success(request, 'Promoción eliminada.')
    return redirect('dashboard')


# ─── TRABAJADORES ─────────────────────────────────────────────────────────────

def agregar_trabajador(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    if request.method == 'POST':
        Trabajador.objects.create(
            locatario=loc,
            nombre=request.POST.get('nombre', ''),
            puesto=request.POST.get('puesto', ''),
            foto=request.FILES.get('foto'),
        )
        messages.success(request, 'Trabajador agregado.')
    return redirect('dashboard')


def editar_trabajador(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    trab = get_object_or_404(Trabajador, pk=pk, locatario=loc)
    if request.method == 'POST':
        trab.nombre = request.POST.get('nombre', trab.nombre)
        trab.puesto = request.POST.get('puesto', trab.puesto)
        if request.FILES.get('foto'):
            trab.foto = request.FILES.get('foto')
        trab.save()
        messages.success(request, 'Trabajador actualizado.')
    return redirect('dashboard')


def eliminar_trabajador(request, pk):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    get_object_or_404(Trabajador, pk=pk, locatario=loc).delete()
    messages.success(request, 'Trabajador eliminado.')
    return redirect('dashboard')


# ─── FOTOS DEL LOCAL (galería en MongoDB) ─────────────────────────────────────

def subir_foto(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        if foto:
            contenido = base64.b64encode(foto.read()).decode('utf-8')
            fotos_puestos.insert_one({
                'locatario_id': loc.pk,
                'nombre_archivo': foto.name,
                'tipo': foto.content_type,
                'datos_b64': contenido,
            })
            messages.success(request, 'Foto subida correctamente.')
    return redirect('dashboard')


def eliminar_foto(request, foto_id):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    from bson import ObjectId
    fotos_puestos.delete_one({'_id': ObjectId(foto_id), 'locatario_id': loc.pk})
    messages.success(request, 'Foto eliminada.')
    return redirect('dashboard')


# ─── SOLICITUDES DE CAMBIO (texto y fotos, requieren aprobación admin) ────────

def solicitar_cambio(request):
    loc = get_loc_session(request)
    if not loc:
        return redirect('login')
    if request.method == 'POST':
        tipo   = request.POST.get('tipo')
        imagen = request.FILES.get('valor_imagen')

        # Cambios de foto: se guarda la imagen pendiente y la aprueba el admin
        if tipo in ('foto_perfil', 'foto_local'):
            if not imagen:
                messages.error(request, 'Selecciona la nueva imagen.')
                return redirect('dashboard')
            SolicitudCambio.objects.create(
                locatario=loc,
                tipo=tipo,
                valor_imagen=imagen,
            )
            messages.success(request, 'Solicitud de cambio de foto enviada al administrador.')
        else:
            SolicitudCambio.objects.create(
                locatario=loc,
                tipo=tipo,
                valor_nuevo=request.POST.get('valor_nuevo', ''),
            )
            messages.success(request, 'Solicitud de cambio enviada al administrador.')
    return redirect('dashboard')


# ─── PANEL ADMIN ──────────────────────────────────────────────────────────────

ADMIN_USER = 'admin'
ADMIN_PASS = 'mama2233'


def admin_login(request):
    if request.method == 'POST':
        if (request.POST.get('usuario') == ADMIN_USER and
                request.POST.get('contrasena') == ADMIN_PASS):
            request.session['admin'] = True
            return redirect('admin_panel')
        messages.error(request, 'Credenciales de administrador incorrectas.')
    return render(request, 'locatarios/admin_login.html')


def admin_logout(request):
    request.session.pop('admin', None)
    return redirect('admin_login')


def check_admin(request):
    return request.session.get('admin', False)


def admin_panel(request):
    if not check_admin(request):
        return redirect('admin_login')

    pendientes  = Locatario.objects.filter(estado='pendiente')
    activos     = Locatario.objects.filter(estado='activo')
    suspendidos = Locatario.objects.filter(estado='suspendido')
    solicitudes = SolicitudCambio.objects.filter(aprobada=False).select_related('locatario')

    return render(request, 'locatarios/admin_panel.html', {
        'pendientes': pendientes,
        'activos': activos,
        'suspendidos': suspendidos,
        'solicitudes': solicitudes,
    })


def admin_aprobar(request, pk):
    if not check_admin(request):
        return redirect('admin_login')
    loc = get_object_or_404(Locatario, pk=pk)
    loc.estado = 'activo'
    loc.save()
    messages.success(request, f'{loc.nombre_completo} aprobado.')
    return redirect('admin_panel')


def admin_rechazar(request, pk):
    if not check_admin(request):
        return redirect('admin_login')
    loc = get_object_or_404(Locatario, pk=pk)
    loc.estado = 'suspendido'
    loc.activo = False
    loc.licencia = ''
    loc.save()
    messages.success(request, f'{loc.nombre_completo} suspendido/rechazado.')
    return redirect('admin_panel')


def admin_generar_licencia(request, pk):
    """Genera una licencia única y activa el puesto del locatario."""
    if not check_admin(request):
        return redirect('admin_login')
    loc = get_object_or_404(Locatario, pk=pk)
    licencia = 'LIC-' + str(uuid.uuid4()).upper()[:12]
    loc.licencia = licencia
    loc.activo   = True
    loc.estado   = 'activo'
    loc.save()
    messages.success(request, f'Licencia {licencia} generada para {loc.nombre_completo}.')
    return redirect('admin_panel')


def admin_aprobar_cambio(request, pk):
    if not check_admin(request):
        return redirect('admin_login')
    solicitud = get_object_or_404(SolicitudCambio, pk=pk)
    loc = solicitud.locatario

    # Aplicar el cambio según el tipo
    if solicitud.tipo == 'nombre_negocio':
        loc.nombre_negocio = solicitud.valor_nuevo
    elif solicitud.tipo == 'puesto':
        loc.puesto = solicitud.valor_nuevo
    elif solicitud.tipo == 'descripcion':
        loc.descripcion = solicitud.valor_nuevo
    elif solicitud.tipo == 'ubicacion':
        loc.ubicacion = solicitud.valor_nuevo
    elif solicitud.tipo == 'foto_perfil' and solicitud.valor_imagen:
        loc.foto_perfil = solicitud.valor_imagen
    elif solicitud.tipo == 'foto_local' and solicitud.valor_imagen:
        loc.foto_local = solicitud.valor_imagen

    loc.save()
    solicitud.aprobada = True
    solicitud.save()
    messages.success(request, 'Cambio aplicado correctamente.')
    return redirect('admin_panel')
