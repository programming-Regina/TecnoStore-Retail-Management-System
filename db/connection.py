"""Configuración compartida de las conexiones a MySQL.

Esta capa abre la conexión que usa el DAO. La ubicación de MySQL depende
de la configuración, tanto si la operación comenzó en Tkinter como si
llegó por HTTP a Flask.
"""
import os
import mysql.connector
from mysql.connector import Error 

# =============================================================================
# CONEXION CON LA BD
# =============================================================================
def conectar_bd():
    """Abre una conexión a MySQL con la configuración del entorno.

    Si se indica un servidor remoto, se verifica su identidad mediante
    TLS. El DAO recibe la conexión abierta o None si falla la conexión.
    """
    try:
        parametros = dict(host="127.0.0.1", user="root", password="",
                          database="tecno_store_db", port=3306)
        # Socket local del alojamiento: no atraviesa la red ni requiere TLS.
        if os.environ.get("DB_UNIX_SOCKET"):
            parametros = dict(
                unix_socket=os.environ["DB_UNIX_SOCKET"],
                user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"], connection_timeout=10,
                use_pure=True,
            )
        # Cuando el entorno indica un servidor MySQL por red, usamos TLS.
        elif os.environ.get("DB_HOST"):
            parametros = dict(
                host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"], database=os.environ["DB_NAME"],
                port=int(os.environ.get("DB_PORT", "3306")), connection_timeout=10,
                ssl_ca=os.environ.get("DB_SSL_CA", "/etc/ssl/certs/ca-certificates.crt"),
                ssl_disabled=False, ssl_verify_cert=True, ssl_verify_identity=True,
                use_pure=True,
            )
        conexion = mysql.connector.connect(**parametros)

        if conexion.is_connected():
            return conexion

    except Error as e:
        import sys
        print(f"No se pudo conectar a la base de datos (código {e.errno}).", file=sys.stderr)
        return None

# Cómo usar en las funciones:
# conn = conectar_bd()
# if conn:
#     print("Conexión establecida con éxito.")
#     conn.close()
