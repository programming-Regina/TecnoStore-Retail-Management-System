-- Solo para una base NUEVA y VACÍA seleccionada en Plesk.
SET NAMES utf8mb4;
CREATE TABLE Categoria ( 
    id_categoria INT PRIMARY KEY AUTO_INCREMENT, 
    categoria VARCHAR(50) NOT NULL 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Rol (
    id_rol INT PRIMARY KEY AUTO_INCREMENT, 
    rol VARCHAR(30) NOT NULL UNIQUE -- Se agrega UNIQUE según diseño
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE FormaPago ( 
    id_forma_pago INT PRIMARY KEY AUTO_INCREMENT, 
    forma_pago VARCHAR(30) NOT NULL UNIQUE -- Se agrega UNIQUE según diseño
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Proveedor (
    id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
    razon_social VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    activo TINYINT(1) DEFAULT 1 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* 
=======================================================================
TABLAS DEPENDIENTES (CON CLAVES FORÁNEAS)
=======================================================================
*/
CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT, 
    apellido VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL, 
    -- Se corrige a VARCHAR(255) y se agrega el CHECK del diseño para soportar Hash futuro
    clave VARCHAR(255) NOT NULL CHECK (CHAR_LENGTH(clave) >= 4), 
    id_rol INT NOT NULL, 
    activo TINYINT(1) DEFAULT 1 NOT NULL, -- Baja lógica
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE  Producto (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    id_categoria INT NOT NULL,
    descripcion VARCHAR(100) NOT NULL, 
    marca VARCHAR(50) NOT NULL, 
    precio_compra DECIMAL(10,2) NOT NULL CHECK (precio_compra > 0), 
    precio_venta DECIMAL(10,2) NOT NULL CHECK (precio_venta > precio_compra), 
    stock INT NOT NULL DEFAULT 0, 
    activo TINYINT(1) DEFAULT 1 NOT NULL, 
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Venta ( 
    id_venta INT PRIMARY KEY AUTO_INCREMENT, 
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP, 
    id_forma_pago INT NOT NULL, 
    id_usuario INT NOT NULL, 
    FOREIGN KEY (id_forma_pago) REFERENCES FormaPago(id_forma_pago), 
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 

CREATE TABLE Compra (
    id_compra INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_proveedor INT NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*
=======================================================================
 TABLAS INTERMEDIAS (CON CLAVE COMPUESTA)
 =======================================================================
*/

CREATE TABLE DetalleVenta ( 
    id_venta INT NOT NULL, 
    id_producto INT NOT NULL, 
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0), 
    PRIMARY KEY (id_venta, id_producto), -- Clave primaria compuesta 
    FOREIGN KEY (id_venta) REFERENCES Venta(id_venta), 
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 

CREATE TABLE DetalleCompra (
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    precio_costo DECIMAL(10,2) NOT NULL CHECK (precio_costo > 0),
    cantidad INT NOT NULL CHECK (cantidad > 0),
    PRIMARY KEY (id_compra, id_producto),
    FOREIGN KEY (id_compra) REFERENCES Compra(id_compra),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
