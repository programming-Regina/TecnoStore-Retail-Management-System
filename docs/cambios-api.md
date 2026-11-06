# Registro breve de evolución de la API

## 2026-11-05 — Primer listado de productos

**Objetivo:** consultar el catálogo activo por HTTP reutilizando las capas existentes.

- `api/__init__.py`: nueva entrada Flask (`create_app`) y `GET /api/productos`.
- `logic/inventario.py`: reutiliza `procesar_consulta_stock`; incorpora la opción
  `propagar_errores` para el listado sin filtro.
- `db/dao.py`: el listado conserva la consulta de activos ordenados por descripción.
  Con `propagar_errores=True` informa fallos; por defecto conserva la lista vacía
  que recibe Tkinter. Los recursos se cierran también ante errores de consulta.
- `requirements-api.txt`: dependencias de la API separadas de las académicas.
- `.gitignore`: excluye el entorno local `.venv/`.
- `tests/test_api.py`: verifica contrato, catálogo vacío, fallos de conexión/SQL,
  cierre de recursos, compatibilidad del DAO y rechazo de POST con dobles de prueba.

**Para los diagramas:** agregar cliente HTTP y entrada Flask. Secuencia:
cliente → `listar_productos` → `procesar_consulta_stock` →
`obtener_productos_activos_ordenados` → `conectar_bd` → MySQL.
Flask transforma el resultado a JSON y los fallos de datos a HTTP 503.
Tkinter sigue usando la lógica existente. No cambian entidades, tablas ni relaciones.

**Contrato:** HTTP 200 con `{"productos": [...]}`; cada producto incluye
`id_producto`, `descripcion`, `marca`, `precio_venta` y `stock`.
Los precios DECIMAL se serializan como texto para conservar precisión.
Catálogo vacío: `{"productos": []}`. Fallo de datos: HTTP 503 con
`{"error": "No se pudieron consultar los productos."}`.
No incluye filtros, autenticación, paginación ni operaciones de escritura.

**Ejecución local** (PowerShell, desde la raíz del proyecto):

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-api.txt
.\.venv\Scripts\python -m flask --app api run
```

Consultar `http://127.0.0.1:5000/api/productos` con la base `tecno_store_db`
ya preparada en MySQL local según `db/connection.py`. La API no inicializa ni
carga datos automáticamente. Detener con Ctrl+C.
Referencia: [ejecución de Flask](https://flask.palletsprojects.com/en/stable/quickstart/).

**Verificación repetible:** `.\.venv\Scripts\python -m unittest discover -s tests -v`.
Resultado: 5 pruebas aprobadas con conexiones simuladas y ruta Flask verificada.
MySQL real pendiente: el 2026-11-05 no había servicio accesible en
`127.0.0.1:3306`. No se modificaron datos ni se inició el servidor MySQL.

**Alcance:** trabajo en `feature/rest-api`. No se modifican `main.py`, las vistas,
el SQL ni `requirements.txt`; no se realiza merge a `main`.


## 2026-11-05 — Consulta individual por ID

**Objetivo:** consultar un producto activo sin recuperar todo el catálogo.

- `api/__init__.py`: agrega `GET /api/productos/<int:id_producto>`.
- `logic/inventario.py`: agrega `consultar_producto_activo`; los productos
  inactivos se consideran no encontrados, igual que en el catálogo público.
- `db/dao.py`: reutiliza `obtener_producto_por_id` y su SQL parametrizado.
  Ahora informa explícitamente la falta de conexión y cierra recursos si falla
  la consulta. Conserva los campos y la consulta sin filtro para sus consumidores
  existentes; el filtro de activo pertenece a la nueva función de lógica.

**Contrato:** HTTP 200 con `{"producto": {...}}`, con los mismos cinco campos
públicos y precios como texto que el listado. HTTP 404 con
`{"error": "Producto no encontrado."}` para ID cero, inexistente o inactivo.
HTTP 503 con `{"error": "No se pudo consultar el producto."}` ante fallos de datos.
Los segmentos no enteros o negativos no coinciden con la ruta y Flask devuelve 404.

**Para los diagramas:** cliente → `obtener_producto` (Flask) →
`consultar_producto_activo` (lógica) → `obtener_producto_por_id` (DAO) →
`conectar_bd` → MySQL. La lógica decide si pertenece al catálogo activo;
Flask elige el código HTTP y los campos públicos. Sin cambios al modelo de datos.

**Validación:** 12 pruebas automatizadas aprobadas, incluidas las del listado.
Regina confirmó en el navegador que el listado funciona con su base real.
También se comprobó con el cliente de pruebas Flask conectado a MySQL real:
listado 200, detalle del producto ID 34 con 200 e ID 2147483647 con 404.
Todas fueron consultas de lectura.

**Prueba manual:** reiniciar Flask (Ctrl+C y volver a ejecutar
`.\.venv\Scripts\python -m flask --app api run`) y abrir
`http://127.0.0.1:5000/api/productos/34`, o usar otro ID activo del listado.


## 2026-11-05 — Pruebas manuales y alta de productos

**Pruebas de Regina:** `/api/productos/14` devolvió la memoria Kingston Fury
16GB DDR4 Beast, precio `48000.00` y stock 2. El ID inexistente devolvió
`{"error":"Producto no encontrado."}`. Quedan confirmados ambos casos manuales.

**Objetivo:** agregar `POST /api/productos`, reutilizando el alta existente.

- `api/__init__.py`: recibe exclusivamente `descripcion`, `marca`,
  `precio_compra`, `precio_venta` e `id_categoria` en un objeto JSON.
- `logic/inventario.py`: extiende `gestionar_alta_producto` con la opción
  `retornar_id`. Usa Decimal, valida textos, límites de columnas, precios finitos
  positivos con hasta dos decimales, venta mayor al costo y categoría entera positiva.
  Tkinter conserva su retorno `(éxito, mensaje)`; estas validaciones también se aplican allí.
- `db/dao.py`: extiende `insertar_producto` con `retornar_id`. Devuelve el ID tras
  confirmar la transacción; conserva el booleano por defecto para el escritorio.
  Revierte la transacción ante fallos y cierra los recursos.
- Stock inicial 0 y activo 1 se fijan en el DAO; el cliente no puede asignarlos.
  La clave foránea de MySQL comprueba la existencia de la categoría.

**Contrato:** 201 con `{"id_producto": ID, "mensaje": "Producto registrado. Stock inicial: 0."}`
y cabecera `Location: /api/productos/ID`. 400 por JSON o datos inválidos y categoría
inexistente, 415 si no se envía JSON, 409 por otros conflictos de integridad y 503
por fallo de acceso a datos. Los detalles internos no aparecen en la respuesta.

**Para los diagramas:** cliente → `crear_producto` (Flask) →
`gestionar_alta_producto` (validaciones) → `insertar_producto` (DAO) → MySQL.
Éxito: commit y respuesta 201; fallo de escritura: rollback y respuesta de error.
Sin cambios a tablas, relaciones, vistas o `main.py`.

**Validación:** 19 pruebas aprobadas. Se verifican el ID y Location, parámetros
SQL, commit, rollback, cierre de recursos, validaciones sin escritura y
compatibilidad del escritorio. El POST usa conexiones simuladas en las pruebas:
no se insertaron productos en la base académica. Alta real pendiente de prueba manual.

**Prueba manual opcional** (crea un producto real con stock cero): reiniciar Flask
y ejecutar en otra terminal PowerShell, eligiendo una categoría existente:

```powershell
$productoPrueba = @{
    descripcion = "Mouse de prueba API"
    marca = "Prueba"
    precio_compra = "1000.00"
    precio_venta = "1500.00"
    id_categoria = 5
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/productos" -Method Post -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($productoPrueba))
```

Con el ID devuelto, consultar `/api/productos/ID` para verificar sus datos.
No enviar el ejemplo repetidamente: cada solicitud exitosa crea otro producto.

**Pendiente:** autenticación y permisos antes de habilitar altas en internet.
El despliegue en Hostinger queda para el final, según lo acordado con Regina.


## 2026-11-05 — Login y permisos de alta

Regina confirmó que el POST manual anterior fue satisfactorio con MySQL real.

- `POST /api/login`: JSON `username` y `clave`; reutiliza `autenticar_usuario`.
  200 con datos públicos del usuario y cookie de sesión; 400 por datos inválidos,
  415 por formato, 401 por credenciales incorrectas o usuario inactivo y 503 por BD.
- `POST /api/logout`: limpia la cookie del cliente y devuelve 200.
- `POST /api/productos`: ahora requiere sesión (401) y rol administrador o
  depositero; vendedor y gerente reciben 403, siguiendo `MENU_ROLES` de Tkinter.
  Antes de cada alta consulta el estado y rol actuales; una baja invalida el acceso.
- `logic/auth.py`: opción `sesion_escritorio=False` evita compartir `USUARIO_ID`
  entre clientes HTTP. El escritorio conserva su comportamiento por defecto.
- `db/dao.py`: consulta de usuario con propagación opcional de errores de conexión
  y cierre de recursos ante fallos. Sin cambios de tablas ni contraseñas de prueba.
- Sesión firmada Flask por cliente, duración una hora, cookie HttpOnly y
  SameSite Strict. Los GET del catálogo siguen públicos.

**Para diagramas:** cliente → login Flask → autenticación existente → DAO → MySQL;
el login establece la sesión. Alta → sesión → `consultar_rol_api` → DAO → MySQL →
validación de rol → alta existente. Nunca se envía la clave en la respuesta/cookie.

**Configuración local:** se genera una clave aleatoria al crear la aplicación;
reiniciar Flask cierra las sesiones existentes. Para el despliegue final configurar
`FLASK_SECRET_KEY` estable y privada, HTTPS y `COOKIE_SECURE=1`. La sesión firmada
se guarda en el cliente: logout borra su cookie, no revoca copias anteriores.
La demo conserva las contraseñas del SQL. Hash de contraseñas, límites de intentos
 y revocación central de sesiones quedan para una evolución posterior.
Referencia: [sesiones Flask](https://flask.palletsprojects.com/en/stable/quickstart/#sessions).

**Pruebas:** 27 automatizadas aprobadas, incluyendo clientes independientes,
credenciales inválidas, inactivos, permisos, cookie inválida y logout.
Con MySQL real: AdminPepe válido 200, clave incorrecta 401, VendedorPepe válido 200,
alta con vendedor 403, logout 200 y alta sin sesión 401. Sin nuevas inserciones.

### Prueba manual actualizada (PowerShell)

Reiniciar Flask. En otra terminal:

```powershell
$loginPrueba = @{ username = "AdminPepe"; clave = "clave" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/login" -Method Post -ContentType "application/json" -Body $loginPrueba -SessionVariable sesionApi
```

Para crear un producto, usar el cuerpo del ejemplo anterior y agregar
`-WebSession $sesionApi` a su `Invoke-RestMethod`. Cada alta exitosa crea un registro real.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/logout" -Method Post -WebSession $sesionApi
```

| Request | Response | Verifica |
| --- | --- | --- |
| POST /api/login, usuario y clave válidos | 200 + usuario + cookie | Inicio de sesión |
| POST /api/login, clave incorrecta | 401 | Credenciales rechazadas |
| POST /api/productos sin cookie | 401 | Sesión requerida |
| POST /api/productos con vendedor | 403 | Permisos por rol |
| POST /api/productos con administrador/depositero y datos válidos | 201 | Alta autorizada (prueba automatizada) |
| POST /api/logout | 200 | Cierre de sesión del cliente |


## 2026-11-05 — Cierre de jornada y pruebas manuales confirmadas

Regina confirmó que las siguientes tres pruebas manuales funcionaron con MySQL
local. Son posteriores a la implementación de autenticación y permisos.

| Request | Response | Verifica |
| --- | --- | --- |
| `POST /api/login` con `AdminPepe` y contraseña incorrecta | 401: credenciales inválidas o usuario inhabilitado | Rechazo de credenciales incorrectas |
| `POST /api/login` con `VendedorPepe` y clave válida; luego `POST /api/productos` con su sesión | Login 200; alta 403: sin permiso para registrar productos | Autenticación exitosa no implica autorización para el alta |
| `POST /api/login` con `AdminPepe` y clave válida; luego `POST /api/productos` con su sesión y datos válidos | Login 200; alta 201, ID generado y stock inicial cero | Alta autorizada y persistencia en MySQL |

**Estado al cierre:** listado, consulta individual, alta, login y logout
implementados. Última ejecución automatizada: 27 pruebas aprobadas.
Las pruebas manuales de listado, detalle existente/inexistente y alta también
fueron confirmadas por Regina. Trabajo local en `feature/rest-api`, sin commit,
merge a `main` ni despliegue. No se agregaron funcionalidades durante este cierre.

**Para retomar el 2026-11-06:** revisar e implementar la modificación de productos
(`PATCH /api/productos/<id>`), después baja lógica y reactivación, manteniendo
permisos de administrador/depositero y las reglas existentes. Documentar y probar
cada operación antes de continuar.

**Mejoras futuras acordadas:** centralizar permisos e incorporar clases de forma
 gradual cuando aporte claridad. La ausencia de clases en la versión inicial
responde a restricciones de las asignaturas en esa etapa. Incorporar esta
justificación al README y a la documentación académica queda pendiente; Regina
lo anotará en sus pendientes. El despliegue en Hostinger se aborda al final.
