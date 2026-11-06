# Registro de cambios — API Tecno Store

Cambios más recientes arriba. Registro breve de lo implementado en la rama `feature/rest-api`.

## 2026-11-06 — Publicación de la rama en GitHub
- Se confirmó el envío de los cambios a `origin/feature/rest-api` (commit `25724a4`).
- La rama local quedó sincronizada con la remota. `main` no se modificó.
- **Próximo paso:** implementar modificación de productos (`PATCH /api/productos/{id}`), luego baja lógica y reactivación. Probar y documentar cada operación.

## 2026-11-05 — Pruebas finales de autenticación y permisos
- Se comprobaron con MySQL real: rechazo de contraseña incorrecta (401), alta denegada al vendedor (403) y alta autorizada al administrador (201).
- Quedaron implementados listado, detalle, alta, login y logout.
- **Pruebas automatizadas:** 27 aprobadas.
- Pendientes de seguridad para un despliegue público: hash de contraseñas, límites de intentos, revocación de sesiones y configuración HTTPS. Hostinger se deja para el final.

## 2026-11-05 — Login y control de acceso
- Se agregaron `POST /api/login` y `POST /api/logout`.
- El alta de productos requiere sesión y rol administrador o depositero; los GET siguen públicos.
- Las sesiones HTTP se mantienen separadas de la sesión de Tkinter.
- Se implementaron cookies de sesión firmadas, HttpOnly y SameSite Strict; para producción faltan una clave estable y `COOKIE_SECURE=1`.

## 2026-11-05 — Alta de productos
- Se agregó `POST /api/productos`, con validación de datos y reutilización de la lógica y el DAO existentes.
- Devuelve 201 e ID del producto; inicia con stock 0 y activo 1.
- Se incorporaron manejo de transacciones, rollback y respuestas de error.
- Se confirmó un alta manual con MySQL real. Antes de agregar autenticación, las pruebas automatizadas llegaron a 19.

## 2026-11-05 — Consulta de producto por ID
- Se agregó `GET /api/productos/{id}`.
- Responde 200 para un producto activo, 404 si no existe o está inactivo y 503 ante fallos de datos.
- Se probaron consultas con MySQL real y en el navegador; las pruebas automatizadas llegaron a 12.

## 2026-11-05 — Primer listado de productos
- Se creó la entrada Flask y `GET /api/productos`.
- La API reutiliza `logic/inventario.py` y `db/dao.py`, sin reemplazar Tkinter ni modificar el modelo de datos.
- Devuelve productos activos en JSON; precios DECIMAL como texto para conservar precisión.
- Se agregaron `requirements-api.txt`, pruebas y exclusión de `.venv/` en `.gitignore`.
- Primeras 5 pruebas automatizadas aprobadas.

## Notas para la documentación
- Arquitectura API: cliente HTTP → Flask → lógica de negocio → DAO → MySQL.
- Para alta: validar sesión y rol antes de invocar la lógica de inventario.
- La versión de escritorio sigue funcionando con Tkinter; no se cambiaron tablas ni relaciones.
- Pendiente: actualizar README y diagramas conforme avance la API, y explicar la evolución gradual hacia clases y permisos centralizados.
- Las pruebas se ejecutan con `python -m unittest discover -s tests -v`; **no requieren pytest**.
