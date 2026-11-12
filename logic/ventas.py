"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: ventas.py
CAPA: Lógica de Negocio (Controlador / Servicios)
DESCRIPCIÓN:
Controla el flujo transaccional del punto de venta: registro de operaciones, 
cálculo de totales, desglose de detalles y afectación directa al stock.
===============================================================================
"""
from db.connection import conectar_bd
from logic.auth import USUARIO_ID
from db.dao import obtener_historial_ventas, obtener_venta_completa

# =============================================================================
# REGISTRO DE VENTA
# =============================================================================
def registrar_venta_transaccion(id_forma_pago, USUARIO_ID, carrito):
    """
    PROPÓSITO: Controla el flujo atómico transaccional de una venta al público. Almacena 
               la cabecera en BD, itera los detalles y asegura el comportamiento ACID global.


    PARÁMETROS:  
        :id_forma_pago: (int) ID del método de pago seleccionado por el cliente.
        :id_usuario: (int) ID del vendedor/usuario en sesión que procesa el POS.
        :carrito: (list) Lista de diccionarios con estructura:
                  [{'id_producto': int, 'cantidad': int, 'precio_unitario': float}, ...]

    RETORNO: 
        :exito: (bool), True si la cabecera, todos los detalles y las reglas de negocio de stock 
                se confirmaron mediante Commit. False si ocurrió un Rollback por error operativo.
    """
    conexion = conectar_bd()
    if not conexion:
        return False

    cursor = conexion.cursor()
    
    try:
        conexion.start_transaction()

        # 1. Ejecutar procedimiento para cabecera de Venta
        cursor.execute("CALL PA_RegistrarVenta(%s, %s)", (id_forma_pago, USUARIO_ID))
        
        # Recuperar ID autoincremental generado para asociar los detalles
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_venta = cursor.fetchone()[0]

        # 2. Insertar transaccionalmente los ítems del carrito
        query_detalle = """
            INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario) 
            VALUES (%s, %s, %s, %s)
        """
        
        for item in carrito:
            cursor.execute(query_detalle, (
                id_venta, 
                item['id_producto'], 
                item['cantidad'], 
                item['precio_unitario']
            ))

        # 3. Confirmación atómica de cambios en la base de datos
        conexion.commit()
        exito = id_venta

    except Exception as e:
        conexion.rollback()
        print(f"Error en la transacción de venta: {e}")
        exito = False
        
    finally:
        cursor.close()
        conexion.close()

    return exito


# =============================================================================
# EL CHANGUITO
# =============================================================================
def calcular_subtotal_memoria(carrito):
    """
    PROPÓSITO: Recorre la lista temporal del carrito y calcula el monto total a cobrar 
               multiplicando cantidades por precios unitarios.


    PARÁMETROS:  
        :carrito: (list) Lista de diccionarios de la transacción actual.

    RETORNO: 
        :total: (float) La sumatoria de todos los subtotales de los ítems.
    """
    total = 0.0
    for item in carrito:
        total += float(item['cantidad']) * float(item['precio_unitario'])
    return total


# =============================================================================
# ANULA UNA VENTA
# =============================================================================
def anular_venta_transaccion(id_venta):
    """
    PROPÓSITO: Revierte una venta iterando los detalles para sortear el Safe Update 
               de MySQL. Restaura el stock y elimina registros (Detalle y Cabecera).


    PARÁMETROS:  
        :id_venta: (int) El identificador único de la factura a anular.

    RETORNO: 
        :exito: (bool) True si todo salió bien, False si hubo un error.
        :mensaje: (str) Mensaje detallado del resultado.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        return False, "Error de conexión a la base de datos."

    # IMPORTANTE: Usar dictionary=True para leer fácil las columnas devueltas
    cursor = conexion.cursor(dictionary=True)
    
    try:
        conexion.start_transaction()

        # Verificar si la venta existe
        cursor.execute("SELECT id_venta FROM Venta WHERE id_venta = %s", (id_venta,))
        if not cursor.fetchone():
            return False, "La factura especificada no existe en los registros."

        # RECUPERAR las cantidades ANTES de borrar el detalle
        cursor.execute("SELECT id_producto, cantidad FROM DetalleVenta WHERE id_venta = %s", (id_venta,))
        productos_a_restaurar = cursor.fetchall()

        # RESTAURAR EL STOCK 
        for item in productos_a_restaurar:
            cursor.execute("""
                UPDATE Producto 
                SET stock = stock + %s 
                WHERE id_producto = %s
            """, (item['cantidad'], item['id_producto']))

        # Eliminar los Hijos
        cursor.execute("DELETE FROM DetalleVenta WHERE id_venta = %s", (id_venta,))

        # Eliminar la Cabecera de la Venta (Padre)
        cursor.execute("DELETE FROM Venta WHERE id_venta = %s", (id_venta,))

        # Confirmamos la operación
        conexion.commit()
        return True, f"Factura #{id_venta} fue anulada. El stock ha sido reintegrado."

    except Exception as e:
        conexion.rollback()        
        print(f"Error crítico en BD al anular: {e}")
        return False, f"La base de datos rechazó la operación: {e}"
        
    finally:
        cursor.close()
        conexion.close()


def obtener_detalle_para_anulacion(id_venta):
    """
    PROPÓSITO: Recupera el desglose completo de artículos de una factura
    invocando la función de persistencia unificada del DAO.
    """
    return obtener_venta_completa(id_venta)


# =============================================================================
# VENTAS HISTÓRICAS
# =============================================================================

def procesar_historial_ventas():
    """ Puente lógico para traer el listado general de ventas """
    return obtener_historial_ventas()

def procesar_detalle_venta(id_venta):
    """ Puente lógico para traer la cabecera y el detalle de una venta específica """
    return obtener_venta_completa(id_venta)