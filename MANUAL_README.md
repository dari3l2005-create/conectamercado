# ConectaMercado 360 - Manual del Proyecto
### Mercado Melchor Ocampo | Prof. Julio César Méndez Calva

---

## ¿Qué hace este proyecto?

Sistema informativo del mercado donde los **clientes** pueden ver los puestos,
productos y promociones sin comprar. Los **locatarios** se registran, gestionan
su información y el **administrador** aprueba cuentas y genera licencias.

---

## ESTRUCTURA DE CARPETAS

```
conectamercado/
├── manage.py
├── db_mongo.py                 ← Conexión a MongoDB (fotos)
├── static/
│   └── styles.css              ← TODOS los estilos del sitio
├── media/                      ← Fotos de perfil subidas
├── mercado_project/
│   ├── settings.py             ← Configuración Django + MySQL + MongoDB
│   ├── urls.py                 ← URLs principales
│   └── wsgi.py
├── core/                       ← App pública (clientes)
│   ├── views.py                ← Vista index y detalle de negocio
│   ├── urls.py
│   └── templates/core/
│       ├── base.html           ← Navbar + mensajes
│       ├── index.html          ← Página principal con grid de puestos
│       └── negocio.html        ← Detalle del puesto
└── locatarios/                 ← App de locatarios y admin
    ├── models.py               ← Tablas MySQL (Locatario, Producto, Promocion, SolicitudCambio)
    ├── views.py                ← Registro, login, dashboard, admin
    ├── urls.py
    └── templates/locatarios/
        ├── base.html
        ├── registro.html       ← Formulario de registro
        ├── login.html          ← Inicio de sesión
        ├── dashboard.html      ← Panel del locatario
        ├── admin_login.html    ← Login del administrador
        └── admin_panel.html    ← Panel de gestión admin
```

---

## EXTENSIONES RECOMENDADAS (VS Code)

Instala estas extensiones en VS Code para trabajar cómodamente:

| Extensión | Para qué sirve |
|-----------|---------------|
| **Python** (Microsoft) | Soporte completo de Python y Django |
| **Django** (Baptiste Darthenay) | Resaltado de sintaxis en templates |
| **SQLite Viewer** | Ver base de datos SQLite si haces pruebas |
| **Thunder Client** | Probar rutas HTTP fácilmente |
| **Pylance** | Autocompletado inteligente |
| **GitLens** | Control de versiones con Git |

---

## PASO 1 - PREPARAR XAMPP (MySQL)

1. Abre el **Panel de Control de XAMPP**
2. Presiona **Start** en **Apache** y **MySQL**
3. Haz clic en **Admin** de MySQL → se abre phpMyAdmin
4. En el menú izquierdo haz clic en **"Nueva"**
5. Nombre de la base de datos: `mercado_melchor_ocampo`
6. Clic en **Crear**

---

## PASO 2 - PREPARAR MONGODB COMPASS

1. Abre **MongoDB Compass**
2. Conéctate a: `mongodb://localhost:27017/`
3. La base de datos `mercado_media` se crea automáticamente al subir la primera foto
4. Verifica que el servicio de MongoDB esté corriendo:
   - Windows: Servicios → MongoDB → Iniciado
   - O desde cmd: `net start MongoDB`

---

## PASO 3 - CREAR Y ACTIVAR ENTORNO VIRTUAL

Abre una terminal en la carpeta `conectamercado/`

```bash
# Crear entorno virtual
python -m venv env

# Activar (Windows)
.\env\Scripts\activate

# Activar (Mac/Linux)
source env/bin/activate
```

Sabrás que está activo cuando veas `(env)` al inicio de la terminal.

> Si PowerShell bloquea la ejecución en Windows:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## PASO 4 - INSTALAR DEPENDENCIAS

Con el entorno activo, ejecuta:

```bash
pip install "django<5.0" mysqlclient pymongo pillow
```

| Paquete | Para qué sirve |
|---------|---------------|
| `django<5.0` | Framework principal |
| `mysqlclient` | Conectar Django con MySQL (XAMPP) |
| `pymongo` | Conectar Python con MongoDB Compass |
| `pillow` | Manejar imágenes (foto de perfil) |

---

## PASO 5 - CREAR LAS TABLAS EN MYSQL

```bash
python manage.py makemigrations
python manage.py migrate
```

Verifica en phpMyAdmin que aparezcan las tablas:
- `locatarios_locatario`
- `locatarios_producto`
- `locatarios_promocion`
- `locatarios_solicitudcambio`

---

## PASO 6 - CORRER EL PROYECTO

```bash
python manage.py runserver
```

Abre tu navegador y entra a:

| URL | Qué es |
|-----|--------|
| `http://127.0.0.1:8000/` | Página pública con todos los puestos |
| `http://127.0.0.1:8000/locatarios/registro/` | Registro de locatario |
| `http://127.0.0.1:8000/locatarios/login/` | Login de locatario |
| `http://127.0.0.1:8000/locatarios/dashboard/` | Panel del locatario |
| `http://127.0.0.1:8000/locatarios/admin/login/` | Login del administrador |
| `http://127.0.0.1:8000/locatarios/admin/panel/` | Panel de administración |

---

## CREDENCIALES DEL ADMINISTRADOR

```
Usuario:    admin
Contraseña: mama2233
```

---

## FLUJO COMPLETO DEL SISTEMA

```
CLIENTE
  └─ Ve el index con puestos activos
  └─ Entra al detalle del puesto (productos, promociones, fotos)

LOCATARIO - REGISTRO
  └─ Llena formulario (nombre, correo, teléfono, contraseña, foto)
  └─ Su estado queda en "pendiente" → NO puede entrar aún

ADMIN - APROBACIÓN
  └─ Ve la solicitud en su panel
  └─ La aprueba → cambia estado a "activo"
  └─ Genera licencia → el puesto aparece en el index

LOCATARIO - DASHBOARD (ya aprobado y con licencia)
  └─ Agrega/edita/elimina productos
  └─ Agrega/edita/elimina promociones
  └─ Sube/elimina fotos del local (se guardan en MongoDB)
  └─ Solicita cambios (nombre, puesto, descripción, ubicación)

ADMIN - CAMBIOS
  └─ Ve las solicitudes de cambio
  └─ Las aprueba → se aplican automáticamente
```

---

## BASES DE DATOS

### MySQL (XAMPP) → datos del locatario
Tabla `locatarios_locatario`:
- nombre_completo, correo, teléfono, contraseña (hash SHA-256)
- nombre_negocio, puesto, descripcion, ubicacion
- estado (pendiente / activo / suspendido)
- licencia (generada por el admin)
- activo (True solo si tiene licencia)

### MongoDB (Compass) → imágenes
Base de datos `mercado_media`:
- Colección `fotos_puestos` → fotos del local en base64
- Colección `fotos_locatario` → referencia a la foto de perfil

---

## ERRORES COMUNES Y SOLUCIONES

| Error | Causa | Solución |
|-------|-------|---------|
| `OperationalError (2002)` | MySQL apagado | Inicia MySQL en XAMPP |
| `Unknown database` | Base no creada | Crea `mercado_melchor_ocampo` en phpMyAdmin |
| `ImproperlyConfigured` | Falta mysqlclient | `pip install mysqlclient` |
| `ModuleNotFoundError: pymongo` | Falta pymongo | `pip install pymongo` |
| `ServerSelectionTimeoutError` | MongoDB apagado | Inicia el servicio de MongoDB |
| `No module named PIL` | Falta Pillow | `pip install pillow` |
| `TemplateDoesNotExist` | Ruta de template mal | Revisa la estructura de carpetas |
| `(env)` no aparece | Entorno no activado | Ejecuta `.\env\Scripts\activate` |

---

## NOTAS IMPORTANTES

- Los estilos de TODAS las interfaces están en `static/styles.css`
- Las imágenes de perfil se guardan en la carpeta `media/perfiles/`
- Las fotos del local se guardan en **MongoDB** como base64
- El administrador NO usa el sistema de autenticación de Django
- La contraseña de locatarios se guarda con hash **SHA-256**
- Para producción cambiar `DEBUG = False` y configurar `ALLOWED_HOSTS`
