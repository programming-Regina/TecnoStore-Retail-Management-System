"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: auth.py
CAPA: Lógica de Negocio (Controlador / Servicios)
DESCRIPCIÓN:
Gestiona la autenticación de usuarios, validación de credenciales, control
de sesiones y verificación de permisos según el rol asignado y estado.
CODER: Regina
===============================================================================
"""

from db.dao import obtener_usuario_por_username

USUARIO_ID = None

# =============================================================================
# VALIDA ACCESO
# =============================================================================
def autenticar_usuario(username_ingresado, clave_ingresada, *, sesion_escritorio=True):
    """
    PROPÓSITO: valida credenciales usando username compuesto.

    CODER: Regina.

    PARÁMETROS:  
    	:username_ingresado: (str) Nombre y apellido     	
        :clave_ingresada: (str) Nombre y apellido    

    RETORNO: 
    	:success: (bool), True si login exitoso
        :nombre: (str),  nombre y apellido
        :rol: (str), en minúsculas. 

    """
    # Elimina espacios
    username_limpio = username_ingresado.strip().replace(" ", "")
    
    usuario = (obtener_usuario_por_username(username_limpio) if sesion_escritorio else
               obtener_usuario_por_username(username_limpio, propagar_errores=True))
    
    if not usuario:
        return {"error": "Usuario inexistente."}
        
    if usuario["activo"] == 0:
        return {"error": "Usuario inhabilitado para el ingreso."}
        
    clave_guardada = usuario["clave"]
    if clave_guardada.startswith(("scrypt:", "pbkdf2:")):
        # Importación diferida: el escritorio anterior no necesita Flask/Werkzeug.
        from werkzeug.security import check_password_hash
        clave_valida = check_password_hash(clave_guardada, clave_ingresada)
    else:
        # Compatibilidad con usuarios existentes de la aplicación de escritorio.
        import hmac
        clave_valida = hmac.compare_digest(clave_guardada.encode(), clave_ingresada.encode())
    if not clave_valida:
        return {"error": "Contraseña incorrecta."}
    
    rol_final = usuario["rol"].lower()
    if rol_final == "admin":
        rol_final = "administrador"
    
    global USUARIO_ID
    if sesion_escritorio:
        USUARIO_ID = usuario["id_usuario"]
        
    return {
        "success": True,
        "nombre": f"{usuario['nombre']} {usuario['apellido']}",
        "rol": rol_final,
        "username": usuario['nombre'] + usuario['apellido'] # para uso interno (no sacar)
    }


def consultar_rol_api(username):
    """Revalida el estado y rol actual sin usar la sesión global de Tkinter."""
    usuario = obtener_usuario_por_username(username, propagar_errores=True)
    if not usuario or not usuario["activo"]:
        return None
    rol = usuario["rol"].lower()
    return "administrador" if rol == "admin" else rol
