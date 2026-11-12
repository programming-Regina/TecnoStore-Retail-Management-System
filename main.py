"""Punto de entrada de la aplicación de escritorio Tecno Store (IFTS16).

Noviembre de 2026

Asignaturas y docentes
- Técnicas de Programación — Ingrid García
- Administración y Gestión de Base de Datos — Lic. Gustavo Escandell
- Modelado y Diseño de Software — Cristian M. Mendez
- PP3: Diseño y Arquitectura de Sistemas — Leandro Binetti

El escritorio inicia en la pantalla de ingreso. Para consultar el catálogo
o registrar un producto, Tkinter llama a funciones de Python en el mismo
proceso. El recorrido es Tkinter → lógica → DAO → base de datos MySQL.

En la versión web, el recorrido es navegador → Flask → lógica → DAO →
MySQL. Flask recibe peticiones HTTP del navegador. Ambas interfaces
comparten las reglas de inventario y el acceso a los datos.
"""

from views.login_view import mostrar_login
from db.init_db import inicializar_entorno_bd


def main():
    print("Iniciando Tecno Store...")

    # Preparamos los objetos de MySQL que usa la aplicación de escritorio.
    exito_bd = inicializar_entorno_bd()
    if not exito_bd:
        print("El sistema no puede arrancar sin la Base de Datos.")
        return 

    mostrar_login()


if __name__ == "__main__":

    main()