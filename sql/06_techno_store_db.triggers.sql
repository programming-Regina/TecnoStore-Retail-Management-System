-- /sql/06_tecno_store_db.triggers.sql
/* ============================================================================
   Trigger 1 - Evitar vender más stock del disponible   
   ========================================================================= */

DELIMITER $$

CREATE TRIGGER TR_ControlStockInsuficiente
BEFORE INSERT ON DetalleVenta
FOR EACH ROW
BEGIN

    DECLARE v_stock_actual INT;

    SELECT stock
    INTO v_stock_actual
    FROM Producto
    WHERE id_producto = NEW.id_producto;

    IF NEW.cantidad > v_stock_actual THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
    END IF;

END$$

DELIMITER ;

/* ============================================================================
   Trigger 2 - Descontar stock automáticamente al vender
   ========================================================================= */

   DELIMITER $$

CREATE TRIGGER TR_DescontarStockVenta
AFTER INSERT ON DetalleVenta
FOR EACH ROW
BEGIN

    UPDATE Producto
    SET stock = stock - NEW.cantidad
    WHERE id_producto = NEW.id_producto;

END$$

DELIMITER ;

/* ============================================================================
   Trigger 3 - Reponer stock automáticamente al registrar compras
   ========================================================================= */

DELIMITER $$

CREATE TRIGGER TR_AumentarStockCompra
AFTER INSERT ON DetalleCompra
FOR EACH ROW
BEGIN
    -- Actualizamos stock, pisamos el costo viejo y recalculamos venta (+40% de margen)
    UPDATE Producto
    SET stock = stock + NEW.cantidad,
        precio_compra = NEW.precio_costo,
        precio_venta = NEW.precio_costo * 1.40
    WHERE id_producto = NEW.id_producto;

END$$

DELIMITER ;