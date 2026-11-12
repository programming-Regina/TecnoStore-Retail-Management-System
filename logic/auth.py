"""Reglas de autenticación compartidas por Tkinter y Flask.

Ambas interfaces comprueban las credenciales y el estado del usuario con
la misma función. Tkinter guarda el identificador en el proceso de
escritorio. Flask registra el nombre de usuario en su propia sesión web.
"""

from db.dao import obtener_usuario_por_username

USUARIO_ID = None

# =============================================================================
# VALIDA ACCESO
# =============================================================================
def autenticar_usuario(username_ingresado, clave_ingresada, *, sesion_escritorio=True):
    """Comprueba las credenciales y devuelve los datos del usuario o un error.

    El nombre de usuario se arma con el nombre y el apellido. Si la cuenta
    está activa y la clave coincide, se devuelve también el rol normalizado.
    """
    # Normalizamos el nombre de usuario para compararlo con el que busca el DAO.
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
        "username": usuario['nombre'] + usuario['apellido'] # Nombre de usuario que se devuelve a la interfaz.
    }


def consultar_rol_api(username):
    """Consulta si la cuenta sigue activa y qué rol tiene al momento del alta web."""
    usuario = obtener_usuario_por_username(username, propagar_errores=True)
    if not usuario or not usuario["activo"]:
        return None
    rol = usuario["rol"].lower()
    return "administrador" if rol == "admin" else rol
