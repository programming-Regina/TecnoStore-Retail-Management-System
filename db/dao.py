"""Acceso a datos de Tecno Store.

El DAO reúne las consultas SQL y las operaciones de escritura en MySQL.
La lógica puede pedir una operación de inventario con la misma llamada
desde ambos recorridos, aunque el resultado se muestre en Tkinter o se
devuelva al navegador como JSON.
"""

from db.connection import conectar_bd

# =============================================================================
# OBTIENE FORMAS DE PAGO
# =============================================================================
def obtener_formas_pago():
    """ PROPÓSITO: Recupera el catálogo dinámico de formas de pago desde la BD. """
    conexion = conectar_bd()
    if not conexion: return {}
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_forma_pago, forma_pago FROM FormaPago")
        # Retorna un diccionario: {"Efectivo": 1, "Tarjeta": 2...}
        return {fila['forma_pago']: fila['id_forma_pago'] for fila in cursor.fetchall()}
    finally:
        cursor.close()
        conexion.close()

# =============================================================================
# BUSCA USUARIO POR NOMBRE
# =============================================================================
def obtener_usuario_por_username(username_ingresado, *, propagar_errores=False):
    """
    PROPÓSITO: genera el username con nombre y apellido y compara con la BD.


    PARÁMETROS:  
    	:username: (str) Nombre y apellido     	

    RETORNO: 
    	:return: Identificador (str).
    
    ERRORES:  (si aplica)
    	:raises: [TipoError] Condición bajo la cual lanza esta excepción.
    """
    conn = conectar_bd()
    if not conn:
        if propagar_errores:
            raise ConnectionError("No se pudo conectar a la base de datos.")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT u.id_usuario, u.nombre, u.apellido, u.clave, u.activo, r.rol
            FROM Usuario u JOIN Rol r ON u.id_rol = r.id_rol
            WHERE LOWER(REPLACE(CONCAT(TRIM(u.nombre), TRIM(u.apellido)), ' ', '')) = LOWER(%s)
        """
        cursor.execute(query, (username_ingresado,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# =============================================================================
# NUEVO USUARIO
# =============================================================================
def insertar_usuario(datos):
    """
    PROPÓSITO: inserta nuevo usuario.


    PARÁMETROS:  
    	:datos: (list): apellido, nombre, clave, id_rol

    RETORNO: 
    	:return: exito (bool).
    
    ERRORES:  (si aplica)
    	:raises: [TipoError] Condición bajo la cual lanza esta excepción.
    """    
    conexion = conectar_bd()
    cursor = conexion.cursor()
    
    query = """
        INSERT INTO Usuario (apellido, nombre, clave, id_rol, activo) 
        VALUES (%s, %s, %s, %s, 1)
    """
    
    try:
        cursor.execute(query, (
            datos[0], 
            datos[1], 
            datos[2], 
            datos[3]
        ))
        conexion.commit()
        exito = True
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar usuario: {e}")
        exito = False
    finally:
        cursor.close()
        conexion.close()
        
    return exito


# =============================================================================
# BUSCA PRODUCTO POR ID
# =============================================================================
def obtener_producto_por_id(id):
    """
    PROPÓSITO: Consulta en la base de datos un producto específico mediante su ID unívoco 
               y mapea las columnas relacionales.


    PARÁMETROS:  
        :id: (int) Identificador único del producto en la tabla Producto.

    RETORNO: 
        :producto: (dict o None), Diccionario indexado por nombre de columna si el registro 
                   existe, o None si no se encuentra en el catálogo.
    """
    conexion = conectar_bd()
    if not conexion:
        raise ConnectionError("No se pudo conectar a la base de datos.")
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT id_producto, id_categoria, descripcion, marca, precio_compra, precio_venta, stock, activo FROM Producto WHERE id_producto = %s"
        cursor.execute(query, (id,))
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# =============================================================================
# LISTA DE PRODUCTOS EN VENTA
# =============================================================================
def listar_proveedores_activos():
    """
    PROPÓSITO: Recupera el catálogo completo de proveedores comerciales vigentes (con alta lógica).
               Utilizado para alimentar dinámicamente Comboboxes de la interfaz.


    PARÁMETROS:  
        Ninguno.

    RETORNO: 
        :proveedores: (list), Lista de diccionarios, donde cada índice representa un proveedor 
                      activo estructurado como {'id_proveedor': int, 'razon_social': str, 'telefono': str}.
    """
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    
    query = "SELECT id_proveedor, razon_social, telefono FROM Proveedor WHERE activo = 1"
    cursor.execute(query)
    
    proveedores = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return proveedores


# =============================================================================
# BUSCADOR DE PRODUCTOS POR NOMBRE (PARTE)
# =============================================================================
def buscar_productos_por_nombre(termino):
    """
    PROPÓSITO: Busca productos activos en el catálogo cuyo nombre o marca coincidan 
               parcialmente con el término de búsqueda ingresado.


    PARÁMETROS:  
        :termino: (str) Palabra o fragmento a buscar.

    RETORNO: 
        :resultados: (list) Lista de diccionarios con los productos encontrados.
    """
    conexion = conectar_bd()
    if not conexion:
        return []
        
    cursor = conexion.cursor(dictionary=True)
    # Usamos LIKE con comodines % para buscar coincidencias parciales
    query = """
        SELECT id_producto, descripcion, marca, precio_venta, stock 
        FROM Producto 
        WHERE activo = 1 AND (descripcion LIKE %s OR marca LIKE %s)
    """
    valor_busqueda = f"%{termino}%"
    cursor.execute(query, (valor_busqueda, valor_busqueda))
    
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return resultados


# =============================================================================
# OBTENER DATOS DE LA VENTA
# =============================================================================
def obtener_venta_completa(id_venta):
    """
    PROPÓSITO: Recupera de forma relacional la cabecera (datos generales) y el 
               detalle (artículos comprados) de una venta específica para su auditoría.


    PARÁMETROS:  
        :id_venta: (int) Identificador único de la venta a buscar.

    RETORNO: 
        :resultado: (dict o None) Diccionario con llaves 'cabecera' y 'detalles', 
                    o None si la factura no existe en la base de datos.
    """  
    conexion = conectar_bd()
    if not conexion:
        return None
        
    cursor = conexion.cursor(dictionary=True)
    
    # Buscar la cabecera uniendo tablas para traer nombres
    query_cabecera = """
        SELECT v.id_venta, v.fecha, concat(u.nombre, ' ', u.apellido) AS vendedor, fp.forma_pago AS forma_pago
        FROM Venta v
        JOIN Usuario u ON v.id_usuario = u.id_usuario
        JOIN FormaPago fp ON v.id_forma_pago = fp.id_forma_pago
        WHERE v.id_venta = %s
    """
    cursor.execute(query_cabecera, (id_venta,))
    cabecera = cursor.fetchone()
    
    # Si la cabecera no existe, la factura no existe.
    if not cabecera:
        cursor.close()
        conexion.close()
        return None
        
    # Buscar los datos de artículos de esa factura
    query_detalles = """
        SELECT p.descripcion, p.marca, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) AS subtotal
        FROM DetalleVenta dv
        JOIN Producto p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = %s
    """
    cursor.execute(query_detalles, (id_venta,))
    detalles = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return {"cabecera": cabecera, "detalles": detalles}


# =============================================================================
# REGISTRA UNA COMPRA
# =============================================================================
def registrar_compra_transaccion(id_proveedor, lista_productos):
    """
    PROPÓSITO: Registra una compra a proveedor. Inserta cabecera y detalles.
               El trigger de la BD actualiza el stock automáticamente.

    Lógica de compras para manejar los cambios de precios: 
    Usamos el modelo de 'Costo de Reposición' onda negocios de retail. 
    En lugar de complicar el código en Python creando lotes separados para cada precio, 
    armamos un Trigger que al registrar una compra, automáticamente hace tres cosas: 
    - suma el nuevo stock al existente, 
    - actualiza el precio de costo del producto al valor de la factura más reciente, 
    - recalcula el precio de venta al público (sumándole un 40% de margen). 
    Así nos aseguramos de que el vendedor siempre facture con el precio actualizado. 
    El historial exacto de cuánto pagamos en el pasado queda guardado en la tabla de detalles 
    de compra (guarda la auditoría! XD)
    """   
    conexion = conectar_bd()
    if not conexion: 
        return False
    
    cursor = conexion.cursor()
    try:
        conexion.start_transaction()
        
        # 1. Insertar Cabecera de Compra (Solo Proveedor y Fecha, acorde al MER)
        cursor.execute("INSERT INTO Compra (id_proveedor, fecha) VALUES (%s, NOW())", 
                       (id_proveedor,))
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_compra = cursor.fetchone()[0]
        
        # 2. Insertar Detalles
        query_detalle = """
            INSERT INTO DetalleCompra (id_compra, id_producto, cantidad, precio_costo) 
            VALUES (%s, %s, %s, %s)
        """
        for prod in lista_productos:
            cursor.execute(query_detalle, (id_compra, prod['id_producto'], prod['cantidad'], prod['precio_costo']))
            
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print(f"Error crítico en BD al registrar compra: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# TRAE PRODUCTOS DE STOCK BAJO
# =============================================================================
def obtener_productos_stock_critico():
    """
    PROPÓSITO: Recupera el listado de productos en estado crítico desde 
    la vista SQL VW_StockCritico.
    """   
    conexion = conectar_bd()
    if not conexion:
        return []
        
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM VW_StockCritico")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al consultar stock crítico: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()        


# =============================================================================
# SACA PRODUCTO DE LA VENTA
# =============================================================================
def dar_baja_logica_producto(id_producto):
    """
    PROPÓSITO: Cambia el estado del producto a inactivo.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: 
        return False
    
    cursor = conexion.cursor()
    try:
        # Si no estuviera el PA, sería un 
        # cursor.execute("UPDATE Producto SET activo = 0 WHERE id_producto = %s", (id_producto,))
        cursor.execute("CALL PA_BajaLogicaProducto(%s)", (id_producto,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conexion.rollback()
        print(f"Error al ejecutar baja lógica: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# PONE PRODUCTO DE LA VENTA -> revierte la anterior
# =============================================================================
def dar_alta_logica_producto(id_producto):
    """
    PROPÓSITO: Cambia el estado del producto a activo (1) para volver a comercializarlo.
    PARÁMETROS:
        :param id_producto: (int) El identificador único del producto.
    RETORNO:
        :return: (bool) True si se actualizó correctamente, False en caso contrario.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: 
        return False
        
    cursor = conexion.cursor()
    try:
        cursor.execute("UPDATE Producto SET activo = 1 WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conexion.rollback()
        print(f"Error al reactivar producto: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()



# =============================================================================
# LISTA DE PRODUCTOS EN VENTA ORDENADOS POR NOMBRE
# =============================================================================
def obtener_productos_activos_ordenados(*, propagar_errores=False, nombre=None):
    """Lee el catálogo activo ordenado por descripción, con filtro opcional por nombre.

    La API pide que se propaguen los errores de conexión para responder
    con un estado HTTP de servicio no disponible.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        if propagar_errores:
            raise ConnectionError("No se pudo conectar a la base de datos.")
        return []
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if nombre:
            cursor.execute("""SELECT * FROM Producto
                WHERE activo = 1 AND LOCATE(LOWER(%s), LOWER(descripcion)) > 0
                ORDER BY descripcion""", (nombre,))
        else:
            cursor.execute("SELECT * FROM Producto WHERE activo = 1 ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        if propagar_errores:
            raise
        print(f"Error: {e}")
        return []
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# =============================================================================
# MUESTRA PRODUCTOS QUITADOS DE LA VENTA
# =============================================================================
def obtener_productos_inactivos():
    """
    PROPÓSITO: Recupera el listado de productos retirados de la venta (activo = 0).
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: 
        return []
        
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Producto WHERE activo = 0 ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al buscar productos inactivos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# DA DE ALTA DE UN NUEVO PRODUCTO (CON STOCK 0)
# =============================================================================
def insertar_producto(descripcion, marca, precio_compra, precio_venta, id_categoria, *, retornar_id=False):
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        if retornar_id:
            raise ConnectionError("No se pudo conectar a la base de datos.")
        return False
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Producto (descripcion, marca, precio_compra, precio_venta, id_categoria, stock, activo)
            VALUES (%s, %s, %s, %s, %s, 0, 1)
        """, (descripcion, marca, precio_compra, precio_venta, id_categoria))
        id_producto = cursor.lastrowid
        conexion.commit()
        return id_producto if retornar_id else cursor.rowcount > 0
    except Exception as e:
        conexion.rollback()
        if retornar_id:
            raise
        print(f"Error al insertar: {e}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


# =============================================================================
# MUESTRA CATEGORIAS (PARA EL LISTADO DE ALTA DE PRODUCTO)
# =============================================================================
def obtener_categorias(*, propagar_errores=False):
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        if propagar_errores:
            raise ConnectionError("No se pudo conectar a la base de datos.")
        return []
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_categoria, categoria FROM Categoria ORDER BY categoria")
        return cursor.fetchall()
    except Exception as e:
        if propagar_errores:
            raise
        print(f"Error al traer categorías: {e}")
        return []
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()



# *****************************************************************************
# *                             REPORTES VARIOS                               *
# *****************************************************************************

# =============================================================================
# MUESTRA RENDIMIENTOS POR MES
# =============================================================================
def obtener_rendimientos_mensuales():
    """
    PROPÓSITO: Consume la vista VW_RendimientosMensuales.
    JUSTIFICACIÓN TÉCNICA: La lógica de cálculo (ventas - costos) está encapsulada en la base.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: return []
    
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM VW_RendimientosMensuales ORDER BY mes DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al leer vista de rendimientos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# VENTAS POR VENDEDOR, AGRuPADAS POR MES
# =============================================================================
def obtener_ventas_agrupadas_por_usuario(nombre_completo):
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: return []
    
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                DATE_FORMAT(v.fecha, '%m-%Y') AS mes_anio, 
                COUNT(v.id_venta) AS cantidad_ventas,
                SUM(dv.cantidad * dv.precio_unitario) AS total_mes
            FROM Venta v
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
            WHERE CONCAT(u.nombre, ' ', u.apellido) = %s
            GROUP BY mes_anio
            ORDER BY v.fecha DESC
        """
        cursor.execute(query, (nombre_completo,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# RENDIMIENTO DE VENDEDORES POR MES (Gerente-only)
# =============================================================================
def obtener_rendimiento_vendedores():
    """
    Retorna el total vendido, costo y margen de ganancia agrupado por vendedor y mes.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: 
        return []
        
    cursor = conexion.cursor(dictionary=True)
    try:
        # las cuentas que las haga sql
        query = """
            SELECT 
                DATE_FORMAT(v.fecha, '%m-%Y') AS mes,
                CONCAT(u.nombre, ' ', u.apellido) AS vendedor,
                SUM(dv.cantidad * dv.precio_unitario) AS total_vendido,
                SUM(dv.cantidad * p.precio_compra) AS costo_total,
                SUM((dv.cantidad * dv.precio_unitario) - (dv.cantidad * p.precio_compra)) AS margen_ganancia
            FROM Venta v
            JOIN Usuario u ON v.id_usuario = u.id_usuario
            JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
            JOIN Producto p ON dv.id_producto = p.id_producto
            GROUP BY mes, vendedor
            ORDER BY v.fecha DESC, total_vendido DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error en consulta de rendimiento de vendedores: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# RANKING DE PRODUCTOS MÁS VENDIDOS
# =============================================================================
def obtener_ranking_productos(limite=10):
    """
    Retorna el Top N de productos más vendidos, sumando cantidades e ingresos.
    """
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion: 
        return []
        
    cursor = conexion.cursor(dictionary=True)
    try:
        # Agrupamos por producto, sumamos cantidades y ordenamos de mayor a menor
        query = """
            SELECT 
                p.descripcion,
                p.marca,
                SUM(dv.cantidad) AS total_unidades,
                SUM(dv.cantidad * dv.precio_unitario) AS ingresos_generados
            FROM DetalleVenta dv
            JOIN Producto p ON dv.id_producto = p.id_producto
            GROUP BY p.id_producto, p.descripcion, p.marca
            ORDER BY total_unidades DESC
            LIMIT %s
        """
        cursor.execute(query, (limite,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error en consulta de ranking de productos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# OBTENER EL VENTAS POR FORMA DE PAGO
# =============================================================================
def obtener_ventas_por_forma_pago():
    """
    Agrupa y suma los ingresos según forma de pago 
    """   
    conexion = conectar_bd()
    if not conexion: 
        return []
        
    cursor = conexion.cursor(dictionary=True)
    try:
        # Usé LEFT JOIN desde FormaPago para incluir métodos con 0 ventas
        query = """
            SELECT 
                fp.forma_pago,
                COUNT(DISTINCT v.id_venta) AS cantidad_ventas,
                IFNULL(SUM(dv.cantidad * dv.precio_unitario), 0) AS total_ingresos
            FROM FormaPago fp
            LEFT JOIN Venta v ON fp.id_forma_pago = v.id_forma_pago
            LEFT JOIN DetalleVenta dv ON v.id_venta = dv.id_venta
            GROUP BY fp.id_forma_pago, fp.forma_pago
            ORDER BY total_ingresos DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener ventas por forma de pago: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# OBTENER EL HISTORIAL DE VENTAS
# =============================================================================
def obtener_historial_ventas():
    """ 
    PROPÓSITO: Recupera todas las cabeceras de venta para la pantalla de historial. 
    """
    conexion = conectar_bd()
    if not conexion: 
        return []
        
    try:
        cursor = conexion.cursor(dictionary=True)
        # La consulta combina la venta, el vendedor y los importes de sus artículos.
        query = """
            SELECT 
                v.id_venta, 
                v.fecha, 
                SUM(d.cantidad * d.precio_unitario) AS total, 
                u.nombre, 
                u.apellido
            FROM Venta v
            LEFT JOIN Usuario u ON v.id_usuario = u.id_usuario
            LEFT JOIN DetalleVenta d ON v.id_venta = d.id_venta
            GROUP BY v.id_venta, v.fecha, u.nombre, u.apellido
            ORDER BY v.fecha DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener el historial de ventas: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# *****************************************************************************
# *                     GESTIÓN DE USUARIOS (ABM)                             *
# *****************************************************************************

# =============================================================================
# OBTENER TODOS LOS USUARIOS
# =============================================================================
def obtener_todos_los_usuarios():
    """Trae todos los usuarios para armar la grilla del Admin."""   
    conexion = conectar_bd()
    if not conexion:
        return []
    try:
        cursor = conexion.cursor(dictionary=True)
        # Traemos todo.
        cursor.execute("SELECT u.id_usuario, u.apellido, u.nombre, u.id_rol, r.rol AS nombre_rol, u.activo FROM Usuario u  INNER JOIN Rol r ON u.id_rol = r.id_rol;")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# NUEVO USUARIO
# =============================================================================
def insertar_usuario(apellido, nombre, clave, id_rol):
    """Alta de usuario."""
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        query = "INSERT INTO Usuario (apellido, nombre, clave, id_rol, activo) VALUES (%s, %s, %s, %s, 1)"
        cursor.execute(query, (apellido, nombre, clave, id_rol))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al insertar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# MODIFICAR USUARIO
# =============================================================================
def modificar_usuario(id_usuario, apellido, nombre, clave, id_rol):
    """Modificación de los datos del usuario."""
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        query = "UPDATE Usuario SET apellido = %s, nombre = %s, clave = %s, id_rol = %s WHERE id_usuario = %s"
        cursor.execute(query, (apellido, nombre, clave, id_rol, id_usuario))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al modificar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# BAJA DE USUARIO
# =============================================================================
def baja_logica_usuario(id_usuario):
    """Baja Lógica: Pasa activo a 0."""
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE Usuario SET activo = 0 WHERE id_usuario = %s", (id_usuario,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error en baja lógica de usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()


# =============================================================================
# REACTIVAR USUARIO
# =============================================================================
def reactivar_usuario(id_usuario):
    """Pasa activo a 1."""
    from db.connection import conectar_bd
    conexion = conectar_bd()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute("UPDATE Usuario SET activo = 1 WHERE id_usuario = %s", (id_usuario,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al reactivar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()

