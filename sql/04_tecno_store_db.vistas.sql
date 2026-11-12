-- /sql/04_tecno_store_db.vistas.sql
/* ============================================================================
   VW_StockCritico
   3. Productos activos con stock menor a 5 unidades
   Roles: Admin, Depositero
   ========================================================================= */

CREATE OR REPLACE VIEW VW_StockCritico AS
SELECT
    id_producto,
    id_categoria,
    descripcion,
    marca,
    precio_venta,
    stock,
    activo
FROM Producto
WHERE stock < 5
  AND activo = 1;


/* ============================================================================
   VW_CostosMensuales
   11. Costos del mes (mercadería comprada)
   Redundante, pero conservada por compatibilidad y motivos afectivos
   Roles: Admin, Gerente
   ========================================================================= */

CREATE OR REPLACE VIEW VW_CostosMensuales AS
SELECT 
    DATE_FORMAT(c.fecha, '%Y-%m') AS mes,
    SUM(dc.cantidad * dc.precio_costo) AS total_costo_compras
FROM Compra c
JOIN DetalleCompra dc ON c.id_compra = dc.id_compra
GROUP BY DATE_FORMAT(c.fecha, '%Y-%m')
ORDER BY mes ASC;


/* ============================================================================
   VW_RendimientosMensuales
   12. Margen bruto (ventas - costos)
   Roles: Admin, Gerente
   ========================================================================= */

CREATE OR REPLACE VIEW VW_RendimientosMensuales AS
SELECT 
    DATE_FORMAT(v.fecha, '%Y-%m') AS mes,    
    SUM(dv.cantidad * dv.precio_unitario) AS total_vendido,    
    SUM(dv.cantidad * p.precio_compra) AS total_costos,    
    SUM((dv.cantidad * dv.precio_unitario) - (dv.cantidad * p.precio_compra)) AS margen_bruto
FROM Venta v
JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
JOIN Producto p ON dv.id_producto = p.id_producto
GROUP BY DATE_FORMAT(v.fecha, '%Y-%m')
ORDER BY mes ASC;


/* ============================================================================
   VW_ProductoMasVendidoPorMes
   13. Producto más vendido por mes
   Roles: Admin, Gerente
   ========================================================================= */

CREATE OR REPLACE VIEW VW_ProductoMasVendidoPorMes AS
WITH RankingVentas AS (
    SELECT 
        DATE_FORMAT(v.fecha, '%Y-%m') AS mes,
        p.id_producto,
        p.descripcion AS producto,
        p.marca,
        SUM(dv.cantidad) AS cantidad_total_vendida,
        RANK() OVER (
            PARTITION BY DATE_FORMAT(v.fecha, '%Y-%m') 
            ORDER BY SUM(dv.cantidad) DESC
        ) AS posicion
    FROM Venta v
    JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
    JOIN Producto p ON dv.id_producto = p.id_producto
    GROUP BY DATE_FORMAT(v.fecha, '%Y-%m'), p.id_producto, p.descripcion, p.marca
)
SELECT 
    mes,
    id_producto,
    producto,
    marca,
    cantidad_total_vendida
FROM RankingVentas
WHERE posicion = 1
ORDER BY mes ASC;