from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Min
from locatarios.models import Locatario, Producto, Promocion, Trabajador, Resena
from db_mongo import fotos_puestos


def index(request):
    puestos = Locatario.objects.filter(estado='activo', activo=True)
    return render(request, 'core/index.html', {'puestos': puestos})


def negocio(request, pk):
    loc = get_object_or_404(Locatario, pk=pk, estado='activo', activo=True)
    productos    = Producto.objects.filter(locatario=loc)
    promociones  = Promocion.objects.filter(locatario=loc)
    trabajadores = Trabajador.objects.filter(locatario=loc)
    resenas      = Resena.objects.filter(locatario=loc)

    fotos = []
    try:
        fotos_raw = list(fotos_puestos.find({'locatario_id': loc.pk}))
        for f in fotos_raw:
            f['foto_id'] = str(f['_id'])
            fotos.append(f)
    except Exception:
        pass

    return render(request, 'core/negocio.html', {
        'loc': loc,
        'productos': productos,
        'promociones': promociones,
        'trabajadores': trabajadores,
        'resenas': resenas,
        'fotos': fotos,
    })


def agregar_resena(request, pk):
    """El cliente deja una reseña (estrellas + comentario). No requiere cuenta."""
    loc = get_object_or_404(Locatario, pk=pk, estado='activo', activo=True)
    if request.method == 'POST':
        nombre = request.POST.get('nombre_cliente', '').strip() or 'Cliente anónimo'
        try:
            calif = int(request.POST.get('calificacion', 5))
        except (TypeError, ValueError):
            calif = 5
        calif = max(1, min(5, calif))
        Resena.objects.create(
            locatario=loc,
            nombre_cliente=nombre,
            calificacion=calif,
            comentario=request.POST.get('comentario', '').strip(),
        )
        messages.success(request, '¡Gracias por tu reseña!')
    return redirect('negocio', pk=loc.pk)


def buscar(request):
    """
    Busca un producto (ej. 'arroz') y devuelve los locatarios que lo tienen,
    ordenados por mejor precio y mejor valoración.
    """
    q = request.GET.get('q', '').strip()
    resultados = []

    if q:
        productos = (Producto.objects
                     .filter(nombre__icontains=q,
                             locatario__estado='activo',
                             locatario__activo=True)
                     .select_related('locatario'))

        # Agrupar por locatario: nos quedamos con el producto más barato que coincide
        por_loc = {}
        for p in productos:
            lid = p.locatario_id
            if lid not in por_loc or p.precio < por_loc[lid]['precio']:
                por_loc[lid] = {
                    'locatario': p.locatario,
                    'producto': p,
                    'precio': p.precio,
                    'rating': p.locatario.promedio_estrellas(),
                    'total_resenas': p.locatario.total_resenas(),
                }
        resultados = list(por_loc.values())

        # Orden: 1) mejor precio (ascendente)  2) mejor valoración (descendente)
        resultados.sort(key=lambda r: (r['precio'], -r['rating']))

    return render(request, 'core/buscar.html', {'q': q, 'resultados': resultados})
