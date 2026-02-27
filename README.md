# Documentación del Sistema de Ventas

Este repositorio contiene un **sistema de ventas** desarrollado en **Django 6** y **Django REST Framework**. El objetivo es ofrecer una API completa para la gestión de usuarios, productos, carrito de compras e informes de facturas, optimizada para un comercio electrónico básico.

---

## 📁 Estructura general del proyecto

```
├── db.sqlite3 (base de datos local para desarrollo)
├── manage.py
├── media/ (archivos subidos)
├── productos/ (posible app adicional)
├── sistema_ventas/ (configuración global de Django)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── ventas_app/ (aplicación principal)
│   ├── models.py
│   ├── views.py (y viewsets/)
│   ├── serializers/ (serializadores REST)
│   ├── urls.py (rutas API)
│   ├── filters.py
│   ├── permission.py
│   ├── tests.py
│   └── migrations/ (historial de esquema)
└── DOCUMENTACION.md (este archivo)
```

---

## 🛠 Tecnologías y dependencias principales

- **Python 3.11+** (recomendado)
- **Django 6.0**
- **Django REST Framework** para construir la API
- **drf-spectacular** + Swagger para documentación automática
- **djangorestframework-simplejwt** para autenticación JWT
- **django-filter** para filtros en listados
- **cloudinary** + `cloudinary_storage` para el manejo de imágenes
- PostgreSQL como base de datos de producción (en `settings.py`)

> El archivo `requirements.txt` (si existe) incluye los paquetes necesarios; instálalos con:
>
> ```bash
> pip install -r requirements.txt
> ```

---

## 🚀 Configuración y puesta en marcha

1. **Clonar el repositorio** y acceder al directorio:
   ```bash
   git clone <url> "Sistema de ventas"
   cd "Sistema de ventas"
   ```
2. **Crear y activar un entorno virtual** (venv, conda, etc.)
3. **Instalar dependencias** (ver arriba)
4. **Variables de entorno**: opcionalmente usar `.env` para
   `SECRET_KEY`, datos de la base de datos o credenciales de Cloudinary.
5. **Migraciones**:
   ```bash
   python manage.py migrate
   ```
6. **Crear un superusuario** (administrador):
   ```bash
   python manage.py createsuperuser
   ```
7. **Iniciar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```
8. **Acceder a** `http://127.0.0.1:8000/api/schema/swagger-ui/` para ver
   la documentación interactiva (Swagger).

> La base de datos por defecto en `settings.py` es PostgreSQL, pero en
> desarrollo se puede usar SQLite modificando `DATABASES`.

---

## 🔐 Autenticación y permisos

- Se utiliza **JWT** (JSON Web Tokens). Se obtienen en:
  - `POST /api/token/` -> `{"username":"...","password":"..."}`
  - `POST /api/token/refresh/` -> refrescar token
- Muchas rutas requieren `Authorization: Bearer <token>`.
- Permisos personalizados en `ventas_app/permission.py`:
  - `IsStaffUser` usa `user.is_staff`
  - `IsOwnerOrReadOnly` controla edición de recursos propios
  - `IsAnonymousUser` sólo para registrar nuevos usuarios

---

## 🧱 Modelos principales

| Modelo            | Descripción principal                                            |
|-------------------|------------------------------------------------------------------|
| `User` (Django)   | Usuarios del sistema (clientes y staff)                          |
| `UserProfile`     | Datos adicionales (documento, dirección, país, estado civil)     |
| `Country`         | Provincias/países usados en perfiles                            |
| `Category`        | Categorías de productos                                          |
| `Brand`           | Marcas de productos                                              |
| `Products`        | Información de productos; precio, stock, imagen, valoración etc. |
| `Valorations`     | Valoraciones (1‑5) de productos                                  |
| `Comments`        | Comentarios de usuarios sobre productos                         |
| `Cart`            | Carrito ligado a cada usuario                                    |
| `CartItem`        | Ítems dentro del carrito                                         |
| `Invoice`         | Factura generada al comprar                                      |
| `DetailPurchase`  | Detalle de cada ítem en la factura                               |

> Más validaciones y lógica (e.g. promedio de valoraciones, stock)
> se encuentran en los serializadores.

---

## 🧾 API – Rutas disponibles

Todas las rutas prefijan `/api/` (ver `sistema_ventas/urls.py` y
`ventas_app/urls.py`). A continuación se listan las principales:

### Autenticación
- `POST /api/token/` – obtener JWT
- `POST /api/token/refresh/` – refrescar JWT
- `POST /api/token/verify/` – verificar token

### Usuarios y perfiles
- `POST /api/registro/` – registro de cliente (anónimo)
- `POST /api/user_admin/` – crear usuarios staff (requiere staff)
- `GET/PATCH /api/user_update_info/update_user/` – leer/editar datos
- `POST /api/user_update_info/update_password/` – cambiar contraseña
- `GET/PATCH /api/user_update_info/update_profile/` – perfil adicional
- `GET/POST /api/provincia/` – administrar provincias (staff)

### Productos, categorías y marcas
- `GET/POST/PUT/DELETE /api/register_category/` – categorías (staff)
- `GET/POST/PUT/DELETE /api/register_brand/` – marcas (staff)
- `GET/POST/PUT/DELETE /api/register_product/` – productos (staff)
  - Filtrado: `?price_min=..&price_max=..&category=...&brand=...`
  - Ordenamiento: `?ordering=price_product`
- `GET/POST /api/valoration_product/` – valorar productos
- `GET/POST/PUT/DELETE /api/comment_add/` – comentarios (propietario)

### Carrito y facturación
- `GET/POST/PUT/DELETE /api/add_item_cart/` – ítems de carrito
- `GET /api/cart_view/` – ver carrito actual
- `POST /api/invoice/generate_invoice/` – generar factura
- `GET /api/invoice/invoices/` – listar facturas propias
- `GET /api/invoice/invoices_details/` – facturas con detalles

> Las rutas `generate_invoice` y la lógica de `CartItem` se encargan de
> restar stock, vaciar carrito y crear registros en `DetailPurchase`.

---

## 🧩 Filtros y utilidades

- `ventas_app/filters.py` define un `ProductsFilterSet` para
  filtrar por rango de precio, categoría y marca.
- `permission.py` contiene permisos reutilizables.
- `signals.py` (si se requiere, revisar) para crear perfil/carrito
  automáticamente al registrar usuarios.

---

## 📦 Integración con servicios externos

- **Cloudinary**: usado para almacenar imágenes de productos.
  Configuración en `settings.py` con claves hardcodeadas (mejor manejar
  via `.env` en producción).

---

## 🧪 Pruebas

- Las pruebas se encuentran en `ventas_app/tests.py`.
- Ejecutar con:
  ```bash
  python manage.py test ventas_app
  ```

(Revisar y ampliar según sean necesarias más pruebas.)

---

## 📝 Notas adicionales

- El proyecto está preparado para ser extendido con una interfaz web o
  móvil que consuma la API.
- Considerar la creación de un `requirements.txt` y la gestión de secret
  keys/variables de entorno antes del despliegue.
- Para documentación en producción, `drf_spectacular` puede servir el
  esquema OpenAPI en `/api/schema/`.

---

💡 **Consejo:** mantén siempre una copia de seguridad de la base de datos
antes de ejecutar migraciones mayores o modificar modelos.

**¡Listo!** Este documento resume la arquitectura y el uso del sistema
de ventas. Actualízalo cuando se introduzcan nuevas funcionalidades.
