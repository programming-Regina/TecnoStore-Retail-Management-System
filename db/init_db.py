"""
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: init_db.py
CAPA: Acceso a Datos / Infraestructura
DESCRIPCIÓN: Script de inicialización automática (Migración). 
             Garantiza que la base de datos, tablas y rutinas existan 
             antes de que la interfaz gráfica intente consumirlas.
"""
import mysql.connector

# =============================================================================
# INICIA EL ENTORNO -> CARGA VIEWS, PROCEDURES Y TRIGGERS
# =============================================================================
def inicializar_entorno_bd():
    """
    PROPÓSITO: Se conecta al motor MySQL genérico, crea la base de datos si no existe,
               y compila los Procedimientos Almacenados y Triggers necesarios.
    PARÁMETROS: Ninguno.
    RETORNO: (bool) True si todo se inicializó bien, False si hubo error crítico.
    """
    try:
        # conecta al motor MySQL, SIN especificar la database 
        conexion = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            port=3306
        )
        cursor = conexion.cursor()

        # Crear Base de Datos
        cursor.execute("CREATE DATABASE IF NOT EXISTS tecno_store_db;")
        cursor.execute("USE tecno_store_db;")

        # =====================================================================
        # PROCEDIMIENTOS ALMACENADOS
        # =====================================================================
        
        # PA_RegistrarVenta
        cursor.execute("DROP PROCEDURE IF EXISTS PA_RegistrarVenta;")
        
        query_proc_venta = """
        CREATE PROCEDURE PA_RegistrarVenta(
            IN p_id_forma_pago INT,
            IN p_id_usuario INT
        )
        BEGIN
            INSERT INTO Venta (id_forma_pago, id_usuario)
            VALUES (p_id_forma_pago, p_id_usuario);
        END
        """
        cursor.execute(query_proc_venta)


        # PA_BajaLogicaProducto
        cursor.execute("DROP PROCEDURE IF EXISTS PA_BajaLogicaProducto;")
        cursor.execute("""
            CREATE PROCEDURE PA_BajaLogicaProducto(
                IN p_id_producto INT
            )
            BEGIN
                UPDATE Producto
                SET activo = 0
                WHERE id_producto = p_id_producto;
            END
        """)

        # =====================================================================
        # TRIGGERS
        # =====================================================================

        # TR_ControlStockInsuficiente
        cursor.execute("DROP TRIGGER IF EXISTS TR_ControlStockInsuficiente;")
        cursor.execute("""
            CREATE TRIGGER TR_ControlStockInsuficiente
            BEFORE INSERT ON DetalleVenta
            FOR EACH ROW
            BEGIN
                DECLARE v_stock_actual INT;

                SELECT stock INTO v_stock_actual
                FROM Producto
                WHERE id_producto = NEW.id_producto;

                IF NEW.cantidad > v_stock_actual THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
                END IF;
            END
        """)


        # TR_DescontarStockVenta
        cursor.execute("DROP TRIGGER IF EXISTS TR_DescontarStockVenta;")
        
        query_trigger_stock = """
        CREATE TRIGGER TR_DescontarStockVenta
        AFTER INSERT ON DetalleVenta
        FOR EACH ROW
        BEGIN
            UPDATE Producto
            SET stock = stock - NEW.cantidad
            WHERE id_producto = NEW.id_producto;
        END
        """
        cursor.execute(query_trigger_stock)


        # TR_AumentarStockCompra
        cursor.execute("DROP TRIGGER IF EXISTS TR_AumentarStockCompra;")
        cursor.execute("""
            CREATE TRIGGER TR_AumentarStockCompra
            AFTER INSERT ON DetalleCompra
            FOR EACH ROW
            BEGIN            
                UPDATE Producto
                SET stock = stock + NEW.cantidad,
                    precio_compra = NEW.precio_costo,
                    precio_venta = NEW.precio_costo * 1.40
                WHERE id_producto = NEW.id_producto;
            END
        """)

        # =====================================================================
        # VISTAS (VIEWS)
        # =====================================================================

        # VW_StockCritico
        cursor.execute("""
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
            WHERE stock < 5 AND activo = 1;
        """)

        # VW_RendimientosMensuales
        cursor.execute("""
            CREATE OR REPLACE VIEW VW_RendimientosMensuales AS
            SELECT 
                DATE_FORMAT(v.fecha, '%Y-%m') AS mes,
                -- Total vendido: Cantidad * Precio de venta (en DetalleVenta)
                SUM(dv.cantidad * dv.precio_unitario) AS total_vendido,
                -- Total costos estimados: Cantidad * Precio de compra actual (en Producto)
                SUM(dv.cantidad * p.precio_compra) AS total_costos,
                -- Ganancia: (Ventas - Costos)
                SUM((dv.cantidad * dv.precio_unitario) - (dv.cantidad * p.precio_compra)) AS ganancia_estimada
            FROM Venta v
            JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
            JOIN Producto p ON dv.id_producto = p.id_producto
            GROUP BY DATE_FORMAT(v.fecha, '%Y-%m')
            ORDER BY mes ASC;
        """)

        conexion.commit()
        print("Entorno de Base de Datos inicializado correctamente.")
        return True

    except Exception as e:
        print(f"Error crítico inicializando la BD: {e}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()