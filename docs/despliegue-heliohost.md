# Despliegue en HelioHost Tommy

La [demo de Tecno Store](https://reginamolares.helioho.st/) usa HTTPS y MariaDB 12.3.3. Se configuró Apache para ejecutar Flask mediante un adaptador CGI. Flask reutiliza la lógica de negocio y el DAO de la aplicación de escritorio.

Se eligió CGI porque el proceso WSGI compartido no podía leer la configuración privada con permisos `600`. El adaptador conserva las rutas de la API y el encabezado `Location` del alta. También consume el cuerpo HTTP antes de llamar a Flask para evitar respuestas incompletas cuando se rechaza un POST antes de leer el JSON.

## Archivos y configuración

| Origen | Destino en el alojamiento | Permisos |
| --- | --- | --- |
| [tecnostore.py](../deploy/heliohost/tecnostore.py) | `httpdocs/tecnostore.py` | `755` |
| [.htaccess-cgi](../deploy/heliohost/.htaccess-cgi) | `httpdocs/.htaccess` | `644` |
| `hosting.py`, `api/`, `db/`, `logic/` y `assets/img/tecno_store_logo.png` | `tecnostore-private/app/`, con la misma estructura | `644` para archivos |
| [config.example.toml](../deploy/heliohost/config.example.toml) | `tecnostore-private/config.toml` | `600` |

1. Se usó Python 3.14 y los módulos Flask y MySQL Connector disponibles en Tommy.
2. Se configuró HTTPS para el dominio y se publicaron los archivos de entrada en `httpdocs/`. La carpeta `tecnostore-private/` está al mismo nivel que `httpdocs/`.
3. Se completó la sección `[environment]` con `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_UNIX_SOCKET` y un valor aleatorio persistente para `FLASK_SECRET_KEY`. El socket del alojamiento es `/var/lib/mysql/mysql.sock`. La configuración con credenciales queda fuera de Git y de la raíz pública.

## Base de datos de prueba

Se creó una base exclusiva en Plesk y un usuario con acceso local restringido a esa base. Para reproducir la instalación sobre una base vacía, se importan en orden:

1. [Estructura](../deploy/heliohost/01-estructura-nueva.sql) y [catálogo de demo](../deploy/heliohost/02-catalogo-demo.sql).
2. Usuarios de prueba para los cuatro roles, con contraseñas únicas guardadas como hashes compatibles con Werkzeug.
3. [Vistas](../sql/04_tecno_store_db.vistas.sql), [procedimientos](../sql/05_tecno_store_db.procedimientos.sql) y [triggers](../sql/06_techno_store_db.triggers.sql).

Se verificó la importación de 10 tablas, cuatro vistas, dos procedimientos y tres triggers. La demo publicada también contiene compras y ventas ficticias.

## Verificación

- Se comprobó la interfaz por HTTPS, con búsqueda por nombre parcial o ID y cinco categorías en el formulario.
- Se verificaron las consultas de catálogo y detalle, el inicio y cierre de sesión y las cookies `Secure`, `HttpOnly` y `SameSite=Strict`.
- Se comprobó el alta con stock cero para administrador y depositero (201), el rechazo para gerente y vendedor (403) y el rechazo sin sesión (401).
- Se verificó que los archivos privados no se sirven por HTTP. Se aprobaron 40 pruebas locales.

El [registro de cambios](cambios-api.md) resume la evolución y los contratos de la API.
