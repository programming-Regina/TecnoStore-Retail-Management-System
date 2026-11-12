"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: usuarios.py
CAPA: Lógica de Negocio (Controlador / Servicios)
DESCRIPCIÓN: ABM de usuarios
===============================================================================
"""

from db.dao import insertar_usuario, modificar_usuario, baja_logica_usuario, reactivar_usuario,obtener_todos_los_usuarios

def obtener_lista_usuarios():
    """Puente para la grilla de la Vista."""
    return obtener_todos_los_usuarios()

def gestionar_alta_usuario(apellido, nombre, clave, id_rol):
    # 1. Validaciones básicas
    if not apellido or not nombre or not clave or not id_rol:
        return False, "Todos los campos son obligatorios para el alta."
    
    # 2. Llamada al DAO
    exito = insertar_usuario(apellido.strip(), nombre.strip(), clave.strip(), int(id_rol))
    
    if exito:
        return True, f"El usuario {nombre} {apellido} fue registrado con éxito."
    else:
        return False, "Ocurrió un error en la base de datos al registrar el usuario."

def gestionar_modificacion_usuario(id_usuario, apellido, nombre, clave, id_rol):
    if not id_usuario or not apellido or not nombre or not clave or not id_rol:
        return False, "Faltan datos para realizar la modificación."
        
    exito = modificar_usuario(id_usuario, apellido.strip(), nombre.strip(), clave.strip(), int(id_rol))
    if exito:
        return True, "Los datos del usuario fueron actualizados."
    else:
        return False, "Ocurrió un error al intentar modificar el usuario."

def gestionar_baja_usuario(id_usuario):
    # Regla de negocio de seguridad: Evitar que el admin N°1 se borre a sí mismo.
    if int(id_usuario) == 1:
        return False, "Operación denegada: No se puede dar de baja al Administrador principal del sistema."
        
    exito = baja_logica_usuario(id_usuario)
    if exito:
        return True, "Usuario dado de baja (Inactivo)."
    else:
        return False, "Error al intentar dar de baja al usuario."
        
def gestionar_reactivacion_usuario(id_usuario):
    exito = reactivar_usuario(id_usuario)
    if exito:
        return True, "Usuario reincorporado al sistema (Activo)."
    else:
        return False, "Error al intentar reactivar al usuario."