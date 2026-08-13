# Tecno Store — Retail Management System

Sistema integral de gestión y Punto de Venta (POS) para comercios minoristas de productos tecnológicos.

## Descripción

Tecno Store es una aplicación de escritorio para la gestión integral de comercios minoristas, desarrollada en Python, Tkinter y MySQL.

El sistema integra ventas, compras, inventario, administración de usuarios y reportes gerenciales en una única plataforma, implementando una arquitectura multicapa que separa la interfaz, la lógica de negocio y el acceso a datos.

>Este proyecto comenzó como un desafío académico y continúa evolucionando, incorporando mejoras de arquitectura, usabilidad y mantenibilidad.


<p align="center">
  <img src="images/captura.jpeg" alt="Pantalla principal de Tecno Store" width="900">
</p>



## Características

- Gestión de usuarios con control de acceso por roles.
- Punto de Venta (POS).
- Gestión de inventario.
- Compras a proveedores.
- Reportes gerenciales.
- Tickets de venta.
- Anulación de facturas con restitución automática del stock.
- Arquitectura multicapa.
- Integridad de datos mediante transacciones, procedimientos almacenados y triggers.



## Funcionalidades Principales

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

## Stack tecnológico
- Python
- Tkinter
- MySQL
- SQL (Stored Procedures, Views y Triggers)

## Conceptos implementados
- Layered Architecture
- DAO Pattern
- ACID Transactions
- Role-Based Access Control (RBAC)
- Soft Delete
- SQL Views
- Stored Procedures
- Database Triggers

## Aspectos destacados

- Arquitectura desacoplada en capas.
- Automatización de reglas de negocio mediante procedimientos almacenados y triggers.
- Control de inventario completamente transaccional.
- Reportes analíticos utilizando vistas SQL.
- Separación entre lógica de negocio y presentación.
- Sistema preparado para incorporar nuevas interfaces sin modificar la lógica existente.

## Roles del Sistema

El menú principal se adapta dinámicamente según quién inicie sesión:

* **👑 Administrador:** Acceso irrestricto a todas las funcionalidades, incluyendo la gestión de credenciales del personal.
* **📈 Gerente:** Acceso enfocado a la auditoría, reportes e indicadores estadísticos del negocio.
* **🤝 Vendedor:** Restringido al registro de operaciones en mostrador (POS), consulta de stock disponible y visualización de sus propias métricas mensuales.
* **🚚 Depositero:** Perfil logístico. Enfocado en el ingreso de mercadería, gestión del catálogo y control de productos activos/inactivos.



## Arquitectura del Software (Modelo Multicapa)

El sistema se estructura en módulos independientes para evitar el acoplamiento:

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


## Guía de Instalación y Despliegue 

### 1. Requisitos Previos
- **Python 3.10+** (Asegurarse de tener Python agregado al `PATH` de Windows).
- **XAMPP o servidor MySQL local** corriendo en el puerto estándar `3306`.
- Usuario MySQL configurado como `root` sin contraseña 

### 2. Configuración de la Base de Datos (Importación Manual)
1. Abra su cliente MySQL (phpMyAdmin, Workbench, DBeaver, etc.).
2. Importe el script **`sql/01_tecno_store_db.estructura.sql`** para construir las tablas.
3. Importe el script **`sql/02_tecno_store_db.cargaData.sql`** para inyectar el **Dataset de Prueba** (usuarios, productos, ventas de ejemplo).

### 3. Instalación de Dependencias
1. Clone el repositorio: `git clone https://github.com/USUARIO/tecno-store.git`
2. Ingrese a la carpeta del proyecto.
3. Haga doble clic en el archivo **`setup.bat`**. Este script creará un entorno virtual aislado (`env`) e instalará automáticamente las dependencias necesarias.

### 4. Ejecución del Sistema
- Haga doble clic en **`ejecutar.bat`**.
- El sistema iniciará la interfaz gráfica.
- *Nota: Para probar el sistema con privilegios máximos, inicie sesión con las credenciales del Administrador.*

## Historia del proyecto

Tecno Store fue desarrollado inicialmente como proyecto integrador para las asignaturas de Programación y Bases de Datos. Tras finalizar la evaluación académica, el proyecto continúa evolucionando como iniciativa personal incorporando mejoras funcionales y de usabilidad.


## Licencia

Este proyecto continúa en desarrollo con fines educativos y de portfolio. Su código fuente se comparte como ejemplo de arquitectura de software, integración entre Python y MySQL y diseño de aplicaciones de escritorio. No destinado a uso comercial.

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/regina-molares/)
