# Registro de cambios — API Tecno Store

Evolución de la API y la demo web en la rama `feature/rest-api`.

## 2026-11-10 — Búsqueda, categorías y despliegue

- Se incorporó el filtro opcional `nombre` en `GET /api/productos`. Busca coincidencias parciales en la descripción de productos activos sin distinguir mayúsculas y minúsculas.
- Se agregaron los modos de búsqueda por nombre e ID. El cambio de modo limpia y enfoca el campo. **Buscar** y **Enter** ejecutan la consulta, y **Ver todos** recupera el catálogo.
- Se agregó `GET /api/categorias` para cargar las opciones del alta. El formulario muestra el nombre y envía el ID numérico. Se incorporaron estados de carga, lista vacía y error con reintento.
- Se publicó la [demo en HelioHost](https://reginamolares.helioho.st/) con HTTPS, MariaDB y un adaptador CGI para Flask. Se configuraron credenciales fuera de la raíz pública y se incorporó soporte para contraseñas con hash en los usuarios de demo.
- Se aprobaron 40 pruebas locales. En el alojamiento se verificaron las consultas, las categorías, las sesiones y los permisos de alta para los cuatro roles. El [despliegue](despliegue-heliohost.md) reúne los pasos y resultados.

## 2026-11-09 — Interfaz web

- Se agregó una pantalla en `GET /` con catálogo, consulta de productos, inicio y cierre de sesión y formulario de alta. Se implementó con HTML, CSS y JavaScript.

## 2026-11-05 — API de productos y sesiones

- Se incorporó Flask como entrada HTTP y se reutilizaron la lógica de negocio y el DAO de la aplicación Tkinter.
- Se implementaron listado de productos activos, consulta por ID y alta con stock inicial cero.
- Se agregaron inicio y cierre de sesión. La API verifica el rol de administrador o depositero para registrar productos.

## Contratos actuales

| Ruta | Entrada | Respuesta |
| --- | --- | --- |
| `GET /api/productos` | `nombre` opcional | 200 con `productos`, ordenados por descripción. Una búsqueda sin coincidencias devuelve una lista vacía. |
| `GET /api/productos/{id}` | ID entero | 200 con `producto` o 404 si no existe o está inactivo. |
| `GET /api/categorias` | — | 200 con `categorias`, ordenadas por nombre. Cada categoría incluye `id_categoria` y `categoria`. |
| `POST /api/productos` | JSON con `descripcion`, `marca`, `precio_compra`, `precio_venta` e `id_categoria` | 201 con `id_producto`, mensaje y encabezado `Location`. |
| `POST /api/login` | JSON con `username` y `clave` | 200 con los datos públicos del usuario y una cookie de sesión. |
| `POST /api/logout` | Cookie de sesión | 200 con confirmación de cierre. |

El catálogo y el detalle exponen `id_producto`, `descripcion`, `marca`, `precio_venta` y `stock`. El precio de venta se devuelve como texto decimal. El alta valida que ambos precios sean positivos, que el de venta supere al de compra y que exista la categoría.

Los POST de login y alta devuelven 415 si el contenido no es JSON y 400 si los datos son inválidos. El login devuelve 401 si las credenciales son inválidas o el usuario está inhabilitado. El alta devuelve 401 sin sesión válida, 403 para roles sin permiso y 409 ante un conflicto de integridad distinto de una categoría inexistente. Los fallos de base de datos devuelven 503.

Las instrucciones de ejecución local y pruebas están en el [README](../README.md).
