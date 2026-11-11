# Tecno Store — Retail Management System

Tecno Store es un sistema de gestión comercial y punto de venta para un comercio minorista de tecnología. Nació como proyecto académico de Programación y Bases de Datos. En Práctica Profesional III se incorporaron una API REST con Flask y una interfaz web para demostrar la evolución del módulo de productos.

<p align="center">
  <img src="images/captura.jpeg" alt="Pantalla principal de Tecno Store en Tkinter" width="720">
</p>

## Aplicación de escritorio

- Gestión de usuarios y permisos para administrador, gerente, vendedor y depositero.
- Inventario con altas, consultas, bajas lógicas y reactivación de productos.
- Compras a proveedores, ventas en mostrador, tickets y anulación de ventas con restitución de stock.
- Reportes de rendimiento, productos vendidos y formas de pago.

Tkinter y Flask reutilizan la lógica de negocio y la capa de acceso a datos (DAO). La base relacional usa transacciones, vistas, procedimientos almacenados y triggers para operaciones como la actualización de stock.

## Demo web y API

La [demo académica](https://reginamolares.helioho.st/) está alojada en HelioHost Tommy. Usa Flask con un adaptador CGI y una base MariaDB con datos de prueba.

La pantalla permite buscar productos activos por **nombre parcial o ID**. Cambiar el modo limpia el campo y **Ver todos** recupera el catálogo. El alta requiere sesión de administrador o depositero, ofrece un desplegable con las categorías de la base y registra el producto con stock inicial cero.

| Método | Ruta | Operación |
| --- | --- | --- |
| GET | `/api/productos` | Lista productos activos. El parámetro opcional `nombre` filtra por descripción parcial sin distinguir mayúsculas. |
| GET | `/api/productos/{id}` | Consulta un producto activo por ID. |
| POST | `/api/productos` | Registra un producto con un rol autorizado. |
| GET | `/api/categorias` | Lista categorías para el formulario de alta. |
| POST | `/api/login` y `/api/logout` | Inicia y cierra la sesión web. |

La evolución se desarrolla en la rama `feature/rest-api`. El [registro de cambios](docs/cambios-api.md) detalla los contratos y las pruebas. La [guía de despliegue](docs/despliegue-heliohost.md) documenta el alojamiento y la verificación pública.

## Ejecución local

Usá Python y un servidor MySQL local. Para una instalación de prueba, creá y seleccioná una base vacía llamada `tecno_store_db` e importá los scripts `01` y `02` de [sql/](sql/). El script `01` recrea tablas. La conexión local se configura en [db/connection.py](db/connection.py).

**Escritorio en Windows.** Ejecutá `setup.bat` para instalar las dependencias y `ejecutar.bat` para abrir la aplicación.

**Web en PowerShell.** Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-api.txt
.\.venv\Scripts\python -m flask --app api run
```

Abrí [http://127.0.0.1:5000/](http://127.0.0.1:5000/). Para usar el puerto 5055, agregá `--port 5055` al último comando.

**Pruebas de la API.** Ejecutá `.\.venv\Scripts\python -m unittest discover -s tests -v`.

---

Proyecto educativo y de portfolio. [LinkedIn de Regina Molares](https://www.linkedin.com/in/regina-molares/).
