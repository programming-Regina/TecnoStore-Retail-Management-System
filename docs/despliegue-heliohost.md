# Tecno Store en HelioHost Tommy

## Estado final verificado — 2026-11-10

Publicado en **https://reginamolares.helioho.st/** con HTTPS válido y MariaDB
12.3.3 del alojamiento. El arranque efectivo es **Apache CGI → CGIHandler →
Flask → lógica → DAO → MariaDB**, autorizado por el titular tras comprobar que
WSGI compartido no podía leer el archivo privado 600. No se modifica Tkinter.
Las secciones posteriores conservan el diagnóstico y las decisiones anteriores;
este estado final reemplaza sus notas de pruebas pendientes.

La contraseña de base fue corregida manualmente por el titular en Plesk y en
config.toml. Se confirmó por solicitudes reales exitosas, sin leer ni imprimir
la nueva contraseña. Configuración fuera de httpdocs, permisos 600. Socket Unix
local confirmado; no se habilita acceso remoto a MariaDB.

Archivos de entrada vigentes:
- `deploy/heliohost/tecnostore.py` → `httpdocs/tecnostore.py`, permisos 755.
- `deploy/heliohost/.htaccess-cgi` → `httpdocs/.htaccess`, permisos 644.
- Código `api`, `db`, `logic`, `hosting.py` y logo dentro de
  `tecnostore-private/app`; configuración en `tecnostore-private/config.toml`.
- La entrada WSGI original se conserva como alternativa; no es el arranque activo.

CGI consume el cuerpo HTTP antes de ejecutar Flask, incluso cuando la API
rechaza una solicitud sin procesar JSON. Evita el cierre de tubería con entrada
pendiente de Apache (AH00574) y respuestas 401 incompletas. Usa memoria hasta
1 MiB y un archivo temporal para cuerpos mayores. Se conservan las URLs y el
Location de los productos sin prefijo del adaptador.

### Resultados públicos

| Prueba | Resultado |
| --- | --- |
| Pantalla, CSS, JavaScript y logo | 200; revisión visual realizada |
| GET /api/productos | 200; 30 productos iniciales, 32 tras pruebas de alta |
| GET /api/productos?nombre=mouse / MoUsE | 200; mismas dos coincidencias |
| Búsqueda sin coincidencias | 200 y lista vacía; mensaje visible |
| GET /api/productos/1 / ID inexistente | 200 / 404 |
| GET /api/categorias | 200; cinco categorías reales en el desplegable |
| POST /api/productos sin sesión | 401 con JSON completo |
| Login inválido | 401 |
| Login de los cuatro roles | 200; cookies Secure, HttpOnly, SameSite Strict |
| Alta como gerente o vendedor | 403 |
| Alta como administrador o depositero | 201, Location correcto y stock 0 |
| Logout y posterior alta | 200 y 401 en los cuatro roles |
| URLs de configuración, código privado y Git | 403/404; no se sirven archivos |

Se conservaron los productos de prueba **31 y 32**, identificados como
`Prueba despliegue HelioHost AdminDemo` y `Prueba despliegue HelioHost DepositeroDemo`.
Los datos históricos de demo siguen cargados. Las claves de usuarios de demo
permanecen en el archivo local ignorado `.deploy-private/demo-credentials.json`;
no se publican en documentación ni Git.

En el navegador se verificaron Buscar, Enter, mayúsculas, ausencia de resultados,
Ver todos, tabla y categorías. **40 pruebas locales aprobadas**, incluyendo
contratos existentes y ejecución CGI con cuerpo de POST mayor a 64 KiB rechazado
sin sesión. JavaScript y `git diff --check` correctos. Sin commit, push ni cambios
en main. CGI inicia un proceso por solicitud: apropiado para esta demo; no se
contrataron servicios adicionales ni se amplió el acceso a secretos.


## Revisión del 2026-11-10

Rama: `feature/rest-api`. La revisión comenzó con el árbol limpio en `945099e`
(`Mejoras de UI`). No se modifica `main`, no se realiza commit ni push.
Tkinter se conserva; se publica solamente la entrada Flask.

Fuentes oficiales consultadas:
- https://wiki.helionet.org/Flask
- https://tommy2-info.heliohost.org/pyinfo/info3.14.py

La página actual de módulos informa Python 3.14.2, Flask 3.1.3,
mysql-connector-python 26.7.0 y Werkzeug 3.1.5. Los resultados cacheados del
buscador mostraban versiones anteriores: se verificó la página actual.
La versión fijada en `requirements.txt` (9.7.0) se conserva para el entorno
local/escritorio. Tommy proporciona los módulos globales: no se asume que permita
instalar el archivo de dependencias ni se necesita Gunicorn bajo Apache/WSGI.
Se utiliza el conector Python puro para evitar la extensión C en subintérpretes.
La compatibilidad final del conector instalado requiere prueba en el alojamiento.

Tommy puede conservar código WSGI en caché hasta dos horas y no ofrece reinicio
WSGI inmediato. No se contratan servicios ni se cambia de plan.

## Archivos y configuración

Distribución propuesta para la raíz del dominio (confirmar ruta en Plesk):

```text
home-del-sitio/
  httpdocs/
    .htaccess
    flask.wsgi
  tecnostore-private/
    config.toml
    app/
      hosting.py
      api/
      db/
      logic/
      assets/img/tecno_store_logo.png
```

El código, SQL y secretos quedan fuera del directorio público. `flask.wsgi`
resuelve las rutas sin nombres de cuenta fijos. `hosting.py` carga únicamente
variables permitidas desde TOML, activa modo producción y exige una clave
persistente y credenciales de base. Cookies Secure, HttpOnly y SameSite Strict;
DEBUG desactivado. `.htaccess` dirige el tráfico a WSGI y exige HTTPS.
No reemplazar archivos de un sitio existente sin revisar y respaldar primero.

`deploy/heliohost/config.example.toml` es una plantilla sin secretos. El archivo
real no se versiona: carpeta privada 700 y archivo 600 cuando el alojamiento lo
permita. Usar un secreto aleatorio de al menos 32 bytes para Flask.
`DB_UNIX_SOCKET` permite conectar con MariaDB en la misma máquina mediante un
socket Unix, sin enviar credenciales por una red. Confirmar la ruta del socket
antes de configurar. Las conexiones a servidores externos con `DB_HOST`
conservan TLS con validación de CA y nombre; no se desactiva la validación.
Sin configuración externa sigue funcionando MySQL local de Tkinter.

## Base nueva y datos de demo

Crear una base exclusiva y vacía desde Plesk, con usuario restringido a esa base.
No importar el script original 01 directamente: contiene `CREATE DATABASE` y
`DROP TABLE`. La variante `deploy/heliohost/01-estructura-nueva.sql` no contiene
esas operaciones y usa InnoDB/utf8mb4. Al no usar IF NOT EXISTS, detecta tablas
preexistentes y evita dar por exitosa una instalación sobre otra base.

Importar, en una base nueva seleccionada, en este orden:

1. `deploy/heliohost/01-estructura-nueva.sql`.
2. `deploy/heliohost/02-catalogo-demo.sql`: roles, categorías, formas de pago y
   30 productos ficticios del dataset público. No incluye personas, teléfonos,
   compras, ventas ni las contraseñas conocidas del dataset original.
3. Usuarios exclusivos de demo con contraseñas aleatorias y hashes privados,
   para verificar administrador, gerente, vendedor y depositero. No guardar ese
   SQL ni las contraseñas en Git o dentro del directorio público.
4. `sql/04_tecno_store_db.vistas.sql`.
5. `sql/05_tecno_store_db.procedimientos.sql`.
6. `sql/06_techno_store_db.triggers.sql`.

El archivo 03 contiene consultas ilustrativas y no es una migración.
Los archivos 04–06 no fijan DEFINER ni nombre de base. Requieren permisos para
vistas, rutinas y triggers; comprobarlos en el alojamiento. El motor debe
soportar CHECK, CTE y funciones de ventana (MariaDB moderno).
La autenticación reconoce hashes Werkzeug scrypt/pbkdf2 y conserva los usuarios
anteriores de escritorio. No se modifican sus claves ni los datos locales.

## Verificación local realizada

- 39 pruebas unittest aprobadas, incluyendo contratos existentes, categorías,
  búsqueda por nombre, configuración WSGI, cookies seguras, conexión por socket,
  TLS remoto y autenticación con hashes/credenciales anteriores.
- En una base temporal aislada de MariaDB 10.4.24 se importaron las variantes
  01–02 y los originales 04–06: 10 tablas, 30 productos, 5 categorías,
  4 vistas, 2 procedimientos y 3 triggers. Sin usuarios con claves públicas.
  Se retiró solamente esa base temporal; la base local original se conserva.

## Verificación pública pendiente

Acceso a Plesk completado. Dominio: `reginamolares.helioho.st` en Tommy2.
MariaDB 12.3.3; socket `/var/lib/mysql/mysql.sock` confirmado en las variables de
phpMyAdmin. Base `reginamolares_tecnostore` y usuario `reginamolares_tecnoapp`,
solo conexiones locales y sin acceso a otras bases (confirmado por el titular).
Se importaron estructura, catálogo, vistas, procedimientos y triggers.
Se cargaron los históricos del dataset a pedido del titular: 30 productos,
5 categorías, 4 roles, 4 formas de pago, 5 proveedores, 6 compras y 12 detalles,
87 ventas y 94 detalles. Usuarios: cuatro de demo activos con hashes y claves
aleatorias, más tres vendedores inactivos para conservar las referencias
históricas. No se importaron las claves públicas del dataset.
Los triggers estaban activos al importar históricos; se restauraron stock y
precios iniciales del catálogo al final de la transacción para evitar aplicar
los movimientos dos veces. El recorrido completo se verificó primero en una
base temporal local y después se confirmaron los conteos en phpMyAdmin remoto.

Archivos subidos y extraídos sin reemplazar la página inicial de Plesk ni cgi-bin.
La segunda versión del paquete usa permisos Unix 644 para archivos de código.
`tecnostore-private/config.toml` se guardó y verificó con permisos 600; contiene
la contraseña de base, la clave persistente de Flask y el socket. La clave de
Flask tiene una copia privada en `tecnostore-private/flask-secret.txt`, también
con permisos 600. Las claves de usuarios de demo están en el archivo local
ignorado `.deploy-private/demo-credentials.json`; no se incluyen en el informe.

La primera visita HTTPS falló por certificado no confiable; no se saltó la
advertencia. Plesk indicó que el dominio aún no tenía certificado instalado.
Con confirmación del titular para los términos, se inició la emisión del
certificado gratuito de Let's Encrypt para el dominio principal, sin extras.
Plesk confirmó el certificado emitido, válido hasta el 8 de febrero de 2027,
con renovación automática. Una conexión TLS estándar desde Python validó el
certificado sin excepciones ni desactivar verificaciones. El navegador integrado
todavía mostró el certificado anterior; no se omitió su advertencia.

Comprobación pública posterior: `/` devuelve 200 con la bienvenida de HelioHost;
`/api/productos` y `/api/categorias` devuelven 404 y `/flask.wsgi/` devuelve 403.
Los archivos `.htaccess` y `flask.wsgi` existen en httpdocs con permisos 644.
Se añadió `AddHandler cgi-script .py`, recomendado por la wiki para el 403.
Los registros del dominio aún no muestran actividad Apache de estas solicitudes.
La aplicación Flask no puede darse por verificada ni el despliegue por terminado.

Hipótesis pendiente de comprobar: activación/recarga de Apache del alojamiento
recién creado. La FAQ indica hasta dos horas para cuentas nuevas y cambios de
dominios; la guía Flask indica hasta dos horas para recarga WSGI. No se cambia
la arquitectura ni se contrata reinicio inmediato. Próximo paso: volver a probar
tras la activación; si persisten 403/404, revisar Apache con soporte antes de
alterar permisos o cambiar a CGI. El certificado y la importación sí finalizaron.

Referencias: https://wiki.helionet.org/FAQ y https://wiki.helionet.org/Flask.

Pruebas de aceptación: HTTPS, pantalla/CSS/JS/logo, catálogo, nombre parcial en
mayúsculas/minúsculas, vacío, detalle existente/404 y categorías; POST sin sesión
401; login válido/inválido; gerente/vendedor 403; administrador/depositero 201,
Location, stock cero y persistencia; logout seguido de POST 401. Verificar
cookies seguras y que config/código/SQL privados no sean accesibles por HTTP.
No declarar despliegue completo hasta verificar estas condiciones en la URL real.


## Diagnóstico posterior del error 500

Apache ya está ejecutando la entrada WSGI. El registro `Apache error` confirma:
`PermissionError: [Errno 13] Permission denied` al leer el archivo privado
`tecnostore-private/config.toml`. No es un error de SQL ni de importación.
El modo WSGI compartido corre con un usuario distinto del propietario; los
permisos 600 impiden la lectura. No se ampliaron permisos ni se expusieron claves.
Se solicitó autorización para evaluar una entrada CGI bajo el usuario de la
cuenta, conservando Flask y las capas existentes. Alternativa: mantener WSGI y
solicitar a HelioHost permisos específicos para el proceso web. El despliegue
sigue incompleto hasta resolver el acceso y ejecutar las pruebas públicas.


## Entrada CGI autorizada y estado actual

El titular autorizó probar CGI conservando Flask. Se agregó
`deploy/heliohost/tecnostore.py` (755, Python 3.14, CGIHandler de wsgiref) y
`deploy/heliohost/.htaccess-cgi` (644, desplegado como httpdocs/.htaccess).
El adaptador mantiene las URLs públicas y Location sin prefijo interno.
La configuración privada conserva modo 600. CGI logró leerla; se corrigió
una sección TOML duplicada por el editor, reemplazando el contenido completo.

Prueba local del adaptador en un directorio temporal: HTML 200, URLs de estáticos
sin prefijo y POST sin sesión 401. En remoto la pantalla ya devuelve HTML 200,
pero catálogo y categorías responden 503. El diagnóstico de MySQL indica 1045.

Se descubrió que la lectura de la contraseña por la herramienta del navegador
había devuelto el marcador de ocultación, no la contraseña real; ese marcador
se guardó por error en config.toml. La comprobación anterior de guardado y
permisos no verificaba la validez de la credencial. Por tanto, la contraseña
real generada inicialmente NO quedó respaldada por el agente. No reutilizar
ese valor ni afirmar que la conexión esté configurada correctamente.

Se dejó al titular el cambio de contraseña en Plesk y la entrada manual del mismo
valor en DB_PASSWORD del archivo privado, sin compartirlo por chat. Los datos,
usuarios y permisos de la base se conservan. Tras completar ese paso deben
verificarse catálogo, categorías, login, logout, roles y altas en la URL pública.
No se declara el despliegue terminado.

El registro de conexión ahora escribe únicamente el código de error en stderr,
sin mensajes del proveedor ni secretos, para no contaminar la respuesta CGI.
