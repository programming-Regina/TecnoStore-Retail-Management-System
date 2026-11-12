"""
===============================================================================
PROYECTO IFTS16: Tecno Store - Sistema de Gestión y Punto de Venta
FECHA:    Noviembre 2026
VERSIÓN:  1.0
PYTHON:   3.x
    
ASIGNATURAS y DOCENTES:
- Técnicas de Programación | DOCENTE:  Ingrid García
- Administración y Gestión de Base de Datos | DOCENTE: Lic. Gustavo Escandell
- Modelado y Diseño de Software | DOCENTE: Cristian M. Mendez
- PP3: Diseño y Arquitectura de Sistemas | DOCENTE: Leandro Binetti  

OBSERVACIÓN:
    Este trabajo práctico se presenta de manera conjunta para varias asignaturas, 
    contando con la previa autorización de sus respectivos docentes. 
    El desarrollo ha sido concebido bajo un enfoque transversal, con el objetivo 
    de demostrar la integración convergente de los saberes de todas las disciplinas 
    en una solución de software, donde los conceptos teóricos y prácticos 
    de cada materia se potencian mutuamente.
-------------------------------------------------------------------------------
ARCHIVO: main.py
DESCRIPCIÓN:
Punto de entrada principal de la aplicación.

Responsabilidades:
- Iniciar la aplicación.
- Mostrar la pantalla de login.
- Mantener el ciclo principal de Tkinter.

IMPORTANTE:
Toda la navegación comienza en LoginView.
===============================================================================
"""

from views.login_view import mostrar_login
from db.init_db import inicializar_entorno_bd


def main():
    print("Iniciando Tecno Store...")

    # prepara el entorno
    exito_bd = inicializar_entorno_bd()
    if not exito_bd:
        print("El sistema no puede arrancar sin la Base de Datos.")
        return 

    mostrar_login()


if __name__ == "__main__":

    main()