"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: inventario.py
CAPA: Lógica de Negocio (Controlador / Servicios)
DESCRIPCIÓN:
Administra las reglas de negocio del inventario: alta/baja lógica de productos,
actualización de stock físico y control de alertas para stock crítico.
CODER ZERO: Regina
===============================================================================
"""

from db.dao import dar_baja_logica_producto, insertar_producto, obtener_productos_activos_ordenados, buscar_productos_por_nombre,dar_alta_logica_producto


# =============================================================================
# QUITA DE LA VENTA UN PRODUCTO
# =============================================================================
def gestionar_baja_logica(id_producto):
    """
    PROPÓSITO: Retira un artículo de comercialización (activo = 0).
    CASO DE USO: Un lote de placas de video presenta riesgo de incendio. 
                 Se frena la venta, pero el stock físico aguarda devolución al proveedor.
    """
    if not isinstance(id_producto, int) or id_producto <= 0:
        return False, "ID de producto inválido. Operación cancelada."
        
    exito = dar_baja_logica_producto(id_producto)
    
    if exito:
        return True, "Producto retirado de comercialización (Baja Lógica aplicada)."
    else:
        return False, "Fallo en la base de datos o el producto no existe."
    

# =============================================================================
# REACTIVA UN PRODUCTO EN EL CATÁLOGO
# =============================================================================
def gestionar_reactivacion_producto(id_producto):
    """
    PROPÓSITO: Puente lógico para volver a comercializar un artículo retirado.
    CODER: Regina
    PARÁMETROS:
        :param id_producto: (int) ID del producto a reactivar.
    RETORNO:
        :return: (tuple) (bool, str) Tupla con el estado de éxito y un mensaje descriptivo.
    """
    if not isinstance(id_producto, int) or id_producto <= 0:
        return False, "ID de producto inválido. Operación cancelada."
        
    exito = dar_alta_logica_producto(id_producto)
    
    if exito:
        return True, "El producto ha sido reincorporado al catálogo exitosamente."
    else:
        return False, "No se pudo reactivar el producto en la base de datos."
    

# =============================================================================
# ALTA DE NUEVO PRODUCTO 
# =============================================================================
def gestionar_alta_producto(desc, marca, costo_txt, venta_txt, cat_txt, *, retornar_id=False):
    """Valida el alta; conserva (éxito, mensaje) para la interfaz de escritorio.

    La API solicita retornar_id: recibe el ID o una excepción de validación/datos.
    """
    from decimal import Decimal, InvalidOperation

    try:
        if not isinstance(desc, str) or not desc.strip() or not isinstance(marca, str) or not marca.strip():
            raise ValueError("La descripción y la marca son obligatorias.")
        if len(desc.strip()) > 100 or len(marca.strip()) > 50:
            raise ValueError("La descripción admite 100 caracteres y la marca 50.")
        try:
            if any(isinstance(v, bool) for v in (costo_txt, venta_txt, cat_txt)):
                raise ValueError
            costo, venta = Decimal(str(costo_txt)), Decimal(str(venta_txt))
            categoria = Decimal(str(cat_txt))
            if not categoria.is_finite() or categoria != categoria.to_integral_value() or not 0 < categoria <= 2147483647:
                raise ValueError
            id_cat = int(categoria)
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Los precios deben ser numéricos y la categoría un entero positivo.") from None
        if not costo.is_finite() or not venta.is_finite():
            raise ValueError("Los precios deben ser números finitos.")
        if costo <= 0 or venta <= 0:
            raise ValueError("Los precios deben ser mayores a cero.")
        if costo > Decimal("99999999.99") or venta > Decimal("99999999.99"):
            raise ValueError("Los precios no pueden superar 99999999.99.")
        if costo != costo.quantize(Decimal("0.01")) or venta != venta.quantize(Decimal("0.01")):
            raise ValueError("Los precios admiten hasta dos decimales.")
        if venta <= costo:
            raise ValueError("El precio de venta debe superar al costo para generar rentabilidad.")
    except ValueError as error:
        if retornar_id:
            raise
        return False, str(error)

    if retornar_id:
        return insertar_producto(desc.strip(), marca.strip(), costo, venta, id_cat, retornar_id=True)
    exito = insertar_producto(desc.strip(), marca.strip(), costo, venta, id_cat)
    return (True, "Producto registrado. Stock inicial: 0.") if exito else (False, "Error en la base de datos.")


# =============================================================================
# CONSULTA GENERAL DE STOCK
# =============================================================================
def procesar_consulta_stock(termino_busqueda=None, *, propagar_errores=False, nombre=None):
    """
    PROPÓSITO: Puente lógico para que el vendedor consulte el stock y precio.
               Filtra por nombre si hay un término, o trae todo el catálogo activo.
    CODER: Regina
    PARÁMETROS:
        :param termino_busqueda: (str) Opcional. Palabra clave a buscar.
        :param propagar_errores: (bool) En listado sin filtro, informa fallos a la API.
    RETORNO:
        :return: (list) Lista de diccionarios con los productos encontrados.
    """
    if termino_busqueda:
        return buscar_productos_por_nombre(termino_busqueda)
    else:
        return obtener_productos_activos_ordenados(propagar_errores=propagar_errores, nombre=nombre)


def consultar_producto_activo(id_producto):
    """Consulta individual del catálogo público; oculta productos inactivos."""
    from db.dao import obtener_producto_por_id

    if id_producto <= 0:
        return None
    producto = obtener_producto_por_id(id_producto)
    if producto is None or not producto["activo"]:
        return None
    return producto


def consultar_categorias():
    """Categorías disponibles para el alta web; informa errores de datos."""
    from db.dao import obtener_categorias
    return obtener_categorias(propagar_errores=True)
