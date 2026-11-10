"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: connection.py
CAPA: Acceso a Datos 
DESCRIPCIÓN:
Módulo centralizado de conexión y gestión de la base de datos relacional.
Abstrae la configuración del motor de base de datos y provee el punto de 
acceso unificado para el ciclo de vida de las conexiones en la aplicación.
CODER: Regina
===============================================================================
"""
# correr en consola "python -m pip install mysql-connector-python"
import os
import mysql.connector
from mysql.connector import Error 

# =============================================================================
# CONEXION CON LA BD
# =============================================================================
def conectar_bd():
    """
    PROPÓSITO: Establece y gestiona la conexión inicial con el motor de base de datos local.
    CODER: Regina
    PARÁMETROS: 
        Ninguno. Usa constantes locales para los parámetros de XAMPP (Puerto 3306).
    RETORNO:     
        :return: Objeto mysql.connector.connection si el enlace es exitoso, o None si falla.
    ERRORES: Captura excepciones de tipo mysql.connector.Error para evitar caídas del sistema.
    """
    try:
        parametros = dict(host="127.0.0.1", user="root", password="",
                          database="tecno_store_db", port=3306)
        # Sin DB_HOST se conserva la conexión local del escritorio.
        if os.environ.get("DB_HOST"):
            parametros = dict(
                host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"], database=os.environ["DB_NAME"],
                port=int(os.environ.get("DB_PORT", "3306")), connection_timeout=10,
                ssl_ca=os.environ.get("DB_SSL_CA", "/etc/ssl/certs/ca-certificates.crt"),
                ssl_disabled=False, ssl_verify_cert=True, ssl_verify_identity=True,
            )
        conexion = mysql.connector.connect(**parametros)

        if conexion.is_connected():
            return conexion

    except Error as e:
        print("No se pudo conectar a la base de datos.")
        return None

# Cómo usar en las funciones:
# conn = conectar_bd()
# if conn:
#     print("Conexión establecida con éxito.")
#     conn.close()
