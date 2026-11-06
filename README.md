# Tecno Store — Retail Management System

Sistema de gestión comercial y punto de venta (POS) en evolución hacia una arquitectura con API REST.

## Descripción

Tecno Store es un sistema de gestión para comercios minoristas de productos tecnológicos. Su base funcional, desarrollada en Python y MySQL, contempla ventas, compras, inventario, usuarios y reportes.

Esta rama está dedicada a incorporar una **API REST con Flask** para exponer operaciones del sistema a clientes HTTP. La versión existente utiliza una interfaz de escritorio con Tkinter; la API constituye una vía de acceso adicional, no una migración ya completada.

<p align="center">
  <img src="images/captura.jpeg" alt="Pantalla principal de Tecno Store" width="900">
</p>



## Capacidades del sistema existente

- Gestión de usuarios con control de acceso por roles.
- Punto de Venta (POS).
- Gestión de inventario.
- Compras a proveedores.
- Reportes gerenciales.
- Tickets de venta.
- Anulación de facturas con restitución automática del stock.
- Arquitectura multicapa.
- Integridad de datos mediante transacciones, procedimientos almacenados y triggers.



## Funcionalidades de la versión existente

### Gestión de Usuarios (Personal)
- Alta, modificación y baja lógica de empleados.
- Asignación de roles de acceso.

### Gestión de Inventario
- Alta de nuevos productos al catálogo.
- **Baja lógica:** Se ocultan de la venta pero se conservan para el historial estadístico.
- Reactivación de productos discontinuados.

### Compras a Proveedores
- Registro de abastecimiento.
- **Automatización:** Actualización inmediata del stock físico en la base de datos tras confirmar la compra.

### Ventas (POS)
- Terminal de punto de venta interactivo.
- Selección de forma de pago.
- Generación y visualización de Ticket.
- Descuento automático de stock (controlado mediante Triggers SQL).
- Anulación de facturas con restitución atómica de inventario.

### Reportes y Analítica
- Rendimientos mensuales.
- Ranking de productos más vendidos.
- Rendimiento mensual por vendedor.
- Análisis de ventas según forma de pago.

## Evolución: API REST

Se está diseñando una interfaz HTTP para ampliar las formas de integración de Tecno Store sin reemplazar su aplicación de escritorio. La propuesta utiliza **Flask** como capa de entrada y reutiliza, cuando sea posible, la lógica de negocio y el acceso a datos existentes.

**Alcance incremental:**

| Método | Ruta | Operación |
| --- | --- | --- |
| `GET` | `/api/productos` | Implementado: listar productos activos |
| `GET` | `/api/productos/{id}` | Implementado: consultar un producto activo por ID |
| `POST` | `/api/productos` | Implementado: registrar un producto |

Los endpoints de consulta responden en JSON. El [registro breve de cambios](docs/cambios-api.md) reúne el contrato, la ejecución local, las pruebas y las notas para actualizar diagramas.

**Arquitectura del primer endpoint:** cliente HTTP → Flask → lógica de negocio → DAO → MySQL. La interfaz Tkinter continuará utilizando las capas existentes.

Esta rama contiene una **funcionalidad en desarrollo**: están disponibles el listado, la consulta por ID y el alta. La API incluye login, logout y permisos para el alta; el despliegue sigue pendiente.

## Tecnologías y estado

| Tecnología | Función | Estado en esta rama |
| --- | --- | --- |
| Python | Lógica de negocio y aplicación | Existente |
| MySQL | Persistencia de datos | Existente |
| SQL (procedimientos, vistas y triggers) | Integridad y operaciones de datos | Existente |
| Tkinter | Interfaz gráfica de escritorio heredada | Existente; se conserva |
| Flask | Exposición de operaciones mediante API REST | Implementado para el listado de productos |
| HTTP y JSON | Solicitudes y respuestas de la API | Implementado para el listado de productos |

## Patrones y conceptos de la versión existente
- Layered Architecture
- DAO Pattern
- ACID Transactions
- Role-Based Access Control (RBAC)
- Soft Delete
- SQL Views
- Stored Procedures
- Database Triggers

## Aspectos destacados de la base existente

- Arquitectura desacoplada en capas.
- Automatización de reglas de negocio mediante procedimientos almacenados y triggers.
- Control de inventario completamente transaccional.
- Reportes analíticos utilizando vistas SQL.
- Separación entre lógica de negocio y presentación.
- Sistema preparado para incorporar nuevas interfaces sin modificar la lógica existente.

## Roles de la aplicación existente

El menú principal se adapta dinámicamente según quién inicie sesión:

* **👑 Administrador:** Acceso irrestricto a todas las funcionalidades, incluyendo la gestión de credenciales del personal.
* **📈 Gerente:** Acceso enfocado a la auditoría, reportes e indicadores estadísticos del negocio.
* **🤝 Vendedor:** Restringido al registro de operaciones en mostrador (POS), consulta de stock disponible y visualización de sus propias métricas mensuales.
* **🚚 Depositero:** Perfil logístico. Enfocado en el ingreso de mercadería, gestión del catálogo y control de productos activos/inactivos.



## Arquitectura actual y evolución propuesta

La base del proyecto mantiene la separación entre presentación, lógica de negocio y acceso a datos. La siguiente estructura describe la base de escritorio; la entrada adicional Flask está en `api/` y su registro de evolución en `docs/cambios-api.md`:

```text
tecno_store/
│
├── main.py                  # Punto de entrada de la aplicación
├── setup.bat                # Instalador automático del entorno
├── ejecutar.bat             # Lanzador del sistema
├── requirements.txt         # Dependencias de Python
│
├── db/                      # Capa de Datos (Data Access Object)
│   ├── connection.py        # Configuración de conexión a MySQL
│   └── dao.py               # Abstracción de consultas SQL
│
├── logic/                   # Capa de Lógica (Reglas de Negocio)
│   ├── auth.py              # Autenticación y roles
│   ├── inventario.py
│   ├── ventas.py            # Transacciones ACID de venta
│   ├── compras.py
│   ├── usuarios.py
│   └── reportes.py          # Formateo de analíticas
│
├── sql/                     # Scripts de Base de Datos
│   ├── 01_tecno_store_db.estructura.sql
│   ├── 02_tecno_store_db.cargaData.sql
│   ├── 03_tecno_store_db.consultas.sql
│   ├── 04_tecno_store_db.vistas.sql
│   ├── 05_tecno_store_db.procedimientos.sql
│   └── 06_tecno_store_db.triggers.sql
│
├── views/                   # Capa de Presentación (Tkinter)
│   ├── login_view.py
│   ├── menu_principal.py
│   └── [...otras vistas...]
│
└── utils/                   # Herramientas auxiliares
    ├── ticket.py
    └── helpers.py
```


## Modelo de Datos

Principales entidades relacionales gestionadas por MySQL:

- `Usuario` | `Rol`
- `Producto` | `Categoría`
- `Proveedor`
- `Compra` | `DetalleCompra`
- `Venta` | `DetalleVenta` | `FormaPago`

**Relaciones clave:** Implementación estricta de integridad referencial. Una venta agrupa múltiples detalles (productos), registrados por un usuario específico y abonados mediante una forma de pago. 


## Instalación y ejecución de la versión de escritorio 

### 1. Requisitos Previos
- **Python 3.10+** (Asegurarse de tener Python agregado al `PATH` de Windows).
- **XAMPP o servidor MySQL local** corriendo en el puerto estándar `3306`.
- Usuario MySQL configurado como `root` sin contraseña 

### 2. Configuración de la Base de Datos (Importación Manual)
1. Abra su cliente MySQL (phpMyAdmin, Workbench, DBeaver, etc.).
2. Importe el script **`sql/01_tecno_store_db.estructura.sql`** para construir las tablas.
3. Importe el script **`sql/02_tecno_store_db.cargaData.sql`** para inyectar el **Dataset de Prueba** (usuarios, productos, ventas de ejemplo).

### 3. Instalación de Dependencias
1. Clone el repositorio: `git clone https://github.com/programming-Regina/TecnoStore-Retail-Management-System.git`
2. Ingrese a la carpeta del proyecto.
3. Haga doble clic en el archivo **`setup.bat`**. Este script creará un entorno virtual aislado (`env`) e instalará automáticamente las dependencias necesarias.

### 4. Ejecución del Sistema
- Haga doble clic en **`ejecutar.bat`**.
- El sistema iniciará la interfaz gráfica.
- *Nota: Para probar el sistema con privilegios máximos, inicie sesión con las credenciales del Administrador.*

## Origen del proyecto

Tecno Store comenzó como un proyecto académico de Programación y Bases de Datos y continúa evolucionando como proyecto personal de portfolio.


## Licencia

Este proyecto continúa en desarrollo con fines educativos y de portfolio. Su código fuente se comparte como ejemplo de arquitectura de software, integración entre Python y MySQL y diseño de aplicaciones de escritorio. No destinado a uso comercial.

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/regina-molares/)
