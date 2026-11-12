/* ============================================================================
CONSULTAS SQL - TECNO STORE
Ordenadas según la matriz de consultas de la documentación del TP
/sql/03_tecno_store_db.consultas.sql
============================================================================ */

/* ============================================================================
CONSULTAS BÁSICAS
============================================================================ */

/* 1. Listar todos los productos activos ordenados por precio de venta
Tipo: Básica
Roles: Admin, Vendedor, Depositero
*/

SELECT id_producto, id_categoria, descripcion, marca, precio_compra, precio_venta, stock
FROM Producto
WHERE activo = 1
ORDER BY precio_venta ASC;

/* 2. Listar usuarios por rol
Tipo: Básica
Roles: Admin
*/

SELECT id_usuario, apellido, nombre, id_rol, activo
FROM Usuario
WHERE id_rol = 3;


/* 3. Productos con stock por debajo del mínimo
Tipo: Básica
Roles: Admin, Depositero
*/

SELECT * FROM VW_StockCritico;

-- Implementado dentro de VW_StockCritico


/* 4. Listar todos los proveedores activos
Tipo: Básica
Roles: Admin, Depositero
*/

SELECT id_proveedor, razon_social, telefono
FROM Proveedor
WHERE activo = 1;

/* 5. Buscar producto por descripción (LIKE)
Tipo: Básica
Roles: Admin, Vendedor, Depositero
*/

SELECT id_producto, id_categoria, descripcion, marca, precio_venta, stock
FROM Producto
WHERE descripcion LIKE '%SSD%';

/* ============================================================================
CONSULTAS JOIN
============================================================================ */

/* 6. Ventas con nombre del vendedor que las registró
Tipo: JOIN
Roles: Admin, Gerente
*/

SELECT 
    v.id_venta AS 'Factura',
    v.fecha AS 'Fecha Venta',
    u.nombre AS 'Nombre Vendedor',
    u.apellido AS 'Apellido Vendedor'
FROM Venta v
INNER JOIN Usuario u ON v.id_usuario = u.id_usuario;

/* 7. Detalle de venta con descripción y precio de cada producto
Tipo: JOIN
Roles: Admin, Vendedor
*/

SELECT 
    dv.id_venta AS 'Nro Venta',
    p.descripcion AS 'Producto',
    p.marca AS 'Marca',
    dv.cantidad AS 'Cantidad',
    dv.precio_unitario AS 'Precio Unitario',
    (dv.cantidad * dv.precio_unitario) AS 'Subtotal'
FROM DetalleVenta dv
INNER JOIN Producto p ON dv.id_producto = p.id_producto;

/* 8. Compras con nombre del proveedor
Tipo: JOIN
Roles: Admin, Depositero
*/

SELECT 
    c.id_compra AS 'Código Compra',
    c.fecha AS 'Fecha Compra',
    prov.razon_social AS 'Proveedor'
FROM Compra c
INNER JOIN Proveedor prov ON c.id_proveedor = prov.id_proveedor;


/* 9.
Historial de ventas
Tipo: JOIN
Roles: Admin
*/

SELECT
    v.id_venta AS 'Nro Venta',
    v.fecha AS 'Fecha',
    CONCAT(u.apellido, ', ', u.nombre) AS 'Vendedor',
    fp.forma_pago AS 'Forma de Pago',
    SUM(dv.cantidad * dv.precio_unitario) AS 'Total'
FROM Venta v
JOIN Usuario u ON v.id_usuario = u.id_usuario
JOIN FormaPago fp ON v.id_forma_pago = fp.id_forma_pago
JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
GROUP BY
    v.id_venta,
    v.fecha,
    u.apellido,
    u.nombre,
    fp.forma_pago
ORDER BY v.fecha DESC;


/* 10. Productos que nunca fueron comprados a ningún proveedor
Tipo: LEFT JOIN + NULL
Roles: Admin, Depositero
*/

SELECT
p.id_producto AS 'Código',
p.descripcion AS 'Producto No Comprado',
p.marca AS 'Marca',
p.stock AS 'Stock Actual (Inicial)'
FROM Producto p
LEFT JOIN DetalleCompra dc ON p.id_producto = dc.id_producto
WHERE dc.id_compra IS NULL;

/* ============================================================================
CONSULTAS GROUP BY / HAVING
============================================================================ */

/* 11. Total vendido por mes
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT
    mes,
    total_vendido
FROM VW_RendimientosMensuales
ORDER BY mes ASC;

-- Implementado dentro de VW_RendimientosMensuales

/* 12. Costos del mes (mercadería comprada)
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT
    mes,
    total_costos
FROM VW_RendimientosMensuales
ORDER BY mes ASC;

-- Implementado dentro de VW_RendimientosMensuales

/* 13. Margen bruto (ventas - costos)
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT
    mes,
    margen_bruto
FROM VW_RendimientosMensuales
ORDER BY mes ASC;

-- Implementado dentro de VW_RendimientosMensuales

/* 14. Producto más vendido por mes
Tipo: GROUP BY - Common Table Expression (CTE).
CTE: WITH genera una tabla temporal adentro de la consulta
y ayuda a simplificar las consultas más complejas
En este caso permite calcular las ventas por producto 
para cada mes y, a partir de esos resultados temporales, 
obtener el producto más vendido de cada período sin repetir 
lógica en la consulta.
Roles: Admin, Gerente
*/

WITH VentasPorMes AS (
    SELECT 
        DATE_FORMAT(v.fecha, '%Y-%m') AS mes,
        p.id_producto,
        p.descripcion,
        SUM(dv.cantidad) AS total_vendido
    FROM DetalleVenta dv
    JOIN Venta v ON dv.id_venta = v.id_venta
    JOIN Producto p ON dv.id_producto = p.id_producto
    GROUP BY DATE_FORMAT(v.fecha, '%Y-%m'), p.id_producto, p.descripcion
),
MaximoPorMes AS (
    SELECT mes, MAX(total_vendido) AS max_cantidad
    FROM VentasPorMes
    GROUP BY mes
)
SELECT vpm.mes, vpm.descripcion, vpm.total_vendido
FROM VentasPorMes vpm
JOIN MaximoPorMes mpm ON vpm.mes = mpm.mes AND vpm.total_vendido = mpm.max_cantidad;



/* 15. Categoría más vendida
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT 
    c.id_categoria, 
    c.categoria AS 'Categoría', 
    SUM(dv.cantidad) AS 'Total Unidades Vendidas'
FROM DetalleVenta dv
INNER JOIN Producto p ON dv.id_producto = p.id_producto
INNER JOIN Categoria c ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.categoria
ORDER BY SUM(dv.cantidad) DESC
LIMIT 1;

/* 16. Cantidad de ventas por mes
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT
DATE_FORMAT(fecha, '%Y-%m') AS mes,
COUNT(id_venta) AS total_ventas
FROM Venta
GROUP BY DATE_FORMAT(fecha, '%Y-%m')
ORDER BY mes ASC;

/* 17. Ticket promedio general
Tipo: GROUP BY
Roles: Admin, Gerente
*/

SELECT
ROUND(AVG(sub.total_venta), 2) AS ticket_promedio_general
FROM (
SELECT id_venta, SUM(cantidad * precio_unitario) AS total_venta
FROM DetalleVenta
GROUP BY id_venta
) AS sub;

/* 18. Categorías con más de N productos activos
Tipo: GROUP BY + HAVING
Roles: Admin, Depositero
*/

SELECT
c.categoria,
COUNT(p.id_producto) AS total_productos_activos
FROM Producto p
JOIN Categoria c ON p.id_categoria = c.id_categoria
WHERE p.activo = 1
GROUP BY c.id_categoria, c.categoria
HAVING COUNT(p.id_producto) > 5;

/* 19. Vendedores con ticket promedio superior a un monto
Tipo: GROUP BY + HAVING
Roles: Admin, Gerente
*/

SELECT
u.id_usuario,
CONCAT(u.apellido, ', ', u.nombre) AS vendedor,
ROUND(AVG(totales_ventas.total_ticket), 2) AS ticket_promedio
FROM (
SELECT id_venta, SUM(cantidad * precio_unitario) AS total_ticket
FROM DetalleVenta
GROUP BY id_venta
) AS totales_ventas
JOIN Venta v ON totales_ventas.id_venta = v.id_venta
JOIN Usuario u ON v.id_usuario = u.id_usuario
JOIN Rol r ON u.id_rol = r.id_rol
WHERE r.rol = 'Vendedor'
GROUP BY u.id_usuario, u.apellido, u.nombre
HAVING ticket_promedio > 50000.00;
-- HAVING ROUND(AVG(totales_ventas.total_ticket), 2) > 50000.00;?

/* 20. Proveedores a los que se compró más de N veces
Dejamos N=1 porque tenemos poquitas compras
Tipo: GROUP BY + HAVING
Roles: Admin, Depositero
*/

SELECT
pr.razon_social,
COUNT(c.id_compra) AS cantidad_compras
FROM Compra c
JOIN Proveedor pr ON c.id_proveedor = pr.id_proveedor
GROUP BY pr.id_proveedor, pr.razon_social
HAVING COUNT(c.id_compra) > 1;

/* ============================================================================
SUBCONSULTAS OBLIGATORIAS
============================================================================ */

/* 21. Producto con el mayor stock actual
Tipo: Subconsulta escalar
Roles: Admin, Depositero
*/

SELECT
id_producto,
descripcion,
marca,
stock
FROM Producto
WHERE stock = (SELECT MAX(stock) FROM Producto);

/* 22. Productos vendidos en ventas pagadas con crédito
Tipo: Subconsulta IN
Roles: Admin, Gerente
*/

SELECT p.id_producto, p.descripcion, p.marca
FROM Producto p
INNER JOIN DetalleVenta dv ON p.id_producto = dv.id_producto
WHERE dv.id_venta IN (
SELECT v.id_venta
FROM Venta v
INNER JOIN FormaPago fp
ON v.id_forma_pago = fp.id_forma_pago
WHERE fp.forma_pago = 'Tarjeta de Crédito'
);

/* 23. Vendedores que tienen al menos una venta registrada
Tipo: Subconsulta EXISTS
Roles: Admin, Gerente
*/

SELECT 
    u.id_usuario,
    u.nombre,
    u.apellido,
    u.id_rol
FROM Usuario u
WHERE EXISTS (
    SELECT 1 
    FROM Venta v 
    WHERE v.id_usuario = u.id_usuario
);

/* 24. Productos cuyo precio supera el promedio de su categoría
Tipo: Subconsulta correlacionada
Roles: Admin, Gerente, Vendedor
*/

SELECT
p1.id_producto,
p1.descripcion,
p1.id_categoria,
p1.precio_venta,
(
SELECT ROUND(AVG(p2.precio_venta), 2)
FROM Producto p2
WHERE p2.id_categoria = p1.id_categoria
) AS promedio_categoria
FROM Producto p1
WHERE p1.precio_venta > (
SELECT AVG(p2.precio_venta)
FROM Producto p2
WHERE p2.id_categoria = p1.id_categoria
);


