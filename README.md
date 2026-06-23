# Tecno Store — Sistema de Gestión y Punto de Venta

Sistema integral de gestión y Punto de Venta (POS) para comercios minoristas de productos tecnológicos.

## Descripción

**Tecno Store** es una aplicación de escritorio diseñada para centralizar, controlar y optimizar los flujos comerciales y logísticos de una tienda tecnológica. Desarrollada como Trabajo Práctico Integrador para las asignaturas **Técnicas de Programación** y **Administración y Gestión de Bases de Datos** del **IFTS N.º 16**.

El proyecto fue diseñado utilizando una estricta **arquitectura por capas** para separar la lógica de negocio, el acceso a persistencia (BBDD) y la interfaz gráfica, garantizando escalabilidad y un código limpio.
<p align="center">
  <img src="images/captura.jpeg" alt="Pantalla principal de Tecno Store" width="900">
</p>



## Objetivos

- Centralizar la información operativa del negocio en tiempo real.
- Mantener la integridad y consistencia de los datos mediante transacciones (ACID).
- Controlar el acceso y la visibilidad de opciones según el perfil del empleado.
- Facilitar la gestión de inventario, abastecimiento y ventas al público.
- Extraer inteligencia de negocio (reportes) para la toma de decisiones gerenciales.



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



## Tecnologías y Principios

- **Backend:** Python 3.10+
- **Frontend:** Tkinter (GUI)
- **Base de Datos:** MySQL
- **Control de Versiones:** Git & GitHub
- **Principios Aplicados:** - Arquitectura por capas y separación de responsabilidades.
  - Baja lógica (`activo = 0`).
  - Control de concurrencia y Transacciones Críticas (`commit` / `rollback`).
  - Extracción de datos vía Vistas SQL (`LEFT JOIN`, `GROUP BY`).



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


## Licencia

Proyecto desarrollado exclusivamente con fines académicos para el Instituto de Formación Técnica Superior N.º 16 (Ciudad Autónoma de Buenos Aires). No destinado a uso comercial.

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/regina-molares/)
