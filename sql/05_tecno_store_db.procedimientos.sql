-- /sql/05_tecno_store_db.procedimientos.sql
/* ============================================================================
   Procedimiento 1: PA_RegistrarVenta
   ========================================================================= */
DELIMITER $$

CREATE PROCEDURE PA_RegistrarVenta(
    IN p_id_forma_pago INT,
    IN p_id_usuario INT
)
BEGIN

    INSERT INTO Venta (
        id_forma_pago,
        id_usuario
    )
    VALUES (
        p_id_forma_pago,
        p_id_usuario
    );

    SELECT LAST_INSERT_ID() AS id_venta_generada;

END$$

DELIMITER ;

-- USO: CALL PA_RegistrarVenta(1, 3);

   /* ============================================================================
   Procedimiento 2: PA_BajaLogicaProducto
   ========================================================================= */

   DELIMITER $$

CREATE PROCEDURE PA_BajaLogicaProducto(
    IN p_id_producto INT
)
BEGIN

    UPDATE Producto
    SET activo = 0
    WHERE id_producto = p_id_producto;

    SELECT
        p_id_producto AS id_producto,
        'Producto dado de baja correctamente' AS resultado;

END$$

DELIMITER ;