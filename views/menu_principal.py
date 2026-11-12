"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: menu_principal.py
CAPA: Vista (views)
DESCRIPCIÓN:
Ventana principal del sistema.

Contiene:
- Menú lateral
- Submenús dinámicos según el rol
- Área central de contenido

Todas las pantallas se cargan dentro del frame de contenido.
===============================================================================
"""

import tkinter as tk

from views.components import *
from views.ventas_view import *
from views.inventario_view import *
from views.compras_view import *
from views.reportes_view import *
from views.usuarios_view import *
from views.consultas_view import *
from logic.auth import USUARIO_ID



# =============================================================================
# OPCIONES DE ESCRITORIO DISPONIBLES SEGÚN EL ROL
# =============================================================================

# El rol define qué opciones muestra Tkinter. En la web, Flask revisa el
# permiso de alta al recibir la petición.
MENU_ROLES = {

    "administrador": {
        "Ventas": [
            ("Nueva venta", mostrar_nueva_venta),
            ("Historial ventas", mostrar_historial_ventas), # próxima mejora
            ("Anular venta", mostrar_anular_venta)
        ],
        "Inventario": [
            ("Consultar stock", mostrar_consulta_stock),
            ("Gestión de productos", mostrar_productos),
            ("Stock crítico", mostrar_stock_critico),
            ("Catálogo Inactivo", mostrar_productos_inactivos)
        ],
        "Compras": [
            ("Registrar compra", mostrar_registrar_compra)#,
            #("Proveedores", mostrar_proveedores)
        ],
        "Reportes": [
            ("Márgenes brutos mensuales", mostrar_rendimientos),
            ("Ranking de productos", mostrar_ranking_productos),
            ("Margen bruto mensual por vendedor", mostrar_rendimiento_vendedor)
        ],
        "Administración": [
            ("Gestión de usuarios", mostrar_gestion_usuarios)#,  
            #("Auditoría SQL Avanzada", mostrar_consultas_avanzadas)
        ]
    },

    "gerente": {
        "Reportes": [
            ("Márgenes brutos mensuales", mostrar_rendimientos),
            ("Ranking de productos", mostrar_ranking_productos),
            ("Margen bruto mensual por vendedor", mostrar_rendimiento_vendedor),
            ("Ventas por forma de pago", mostrar_formas_pago)            
        ]#,
        #"Consultas": [
        #    ("Consultas del Sistema", mostrar_consultas_avanzadas)
        #]
    },

    "vendedor": {
        "Ventas": [
            ("Nueva venta", mostrar_nueva_venta)            
        ],
        "Inventario": [
            ("Consultar stock", mostrar_consulta_stock)#,
            #("Consultas permitidas", mostrar_consultas_avanzadas)
        ],
        "Reportes": [
            ("Mis ventas por mes", mostrar_mis_ventas) # Usa el identificador del vendedor de la sesión.
        ]
    },

    "depositero": {
        "Inventario": [
            ("Gestión de productos", mostrar_productos)            
        ],
        "Compras": [
            ("Registrar compra", mostrar_registrar_compra)#,
            #("Proveedores", mostrar_proveedores)
        ],
        "Reportes": [
            ("Stock crítico", mostrar_stock_critico),
            ("Catálogo Inactivo", mostrar_productos_inactivos),
            ("Consultar stock", mostrar_consulta_stock)    
        #    ("Consultas de Depósito", mostrar_consultas_avanzadas)
        ]
    }
}

# =============================================================================
# CIERRA LA SESION Y VUELVE AL LOGIN
# =============================================================================
def cerrar_sesion(ventana):
    USUARIO_ID = None
    ventana.destroy()
    from views.login_view import mostrar_login
    mostrar_login()


# =============================================================================
# MUESTRA MENU DE OPCIONES A PARTIR DE MENU_ROLES
# =============================================================================
def mostrar_dashboard(frame_contenido):

    limpiar_frame(frame_contenido)

    crear_titulo(
        frame_contenido,
        "Bienvenido a Tecno Store"
    )

    crear_subtitulo(
        frame_contenido,
        "Seleccione una opción desde el menú lateral."
    )


def mostrar_submenu(frame_submenu, frame_contenido, rol, menu, usuario):
    limpiar_frame(frame_submenu)

    titulo = tk.Label(
        frame_submenu,
        text=menu,
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 11, "bold")
    )
    titulo.pack(pady=(10, 10))

    opciones = MENU_ROLES[rol][menu]

    for texto, funcion in opciones:
        # Si la función es mostrar_mis_ventas, le pasa el usuario logueado
        if funcion == mostrar_mis_ventas:
            crear_boton_submenu(frame_submenu, texto, lambda f=funcion: f(frame_contenido, usuario))
        else:
            # Si no, ejecuta la función sin parámetros extra
            crear_boton_submenu(frame_submenu, texto, lambda f=funcion: f(frame_contenido))


# =============================================================================
# MUESTRA EL MENU DE OPCIONES PRINCIPAL 
# =============================================================================
def mostrar_menu_principal(usuario):

    print(f"Sesión iniciada para: {usuario['nombre']}")

    ventana = tk.Tk()

    ventana.title("Tecno Store")
    ventana.geometry("1366x768")
    ventana.configure(bg=COLOR_FONDO)

    try:
        ventana.state("zoomed")
    except:
        pass

    # ============================================================
    # CONTENEDOR MENÚ LATERAL
    # ============================================================

    frame_menu = tk.Frame(
        ventana,
        bg=COLOR_MENU,
        width=260
    )

    frame_menu.pack(
        side="left",
        fill="y"
    )

    frame_menu.pack_propagate(False)

    # ============================================================
    # ZONA SUPERIOR (LOGO + MENÚ PRINCIPAL)
    # ============================================================

    frame_menu_superior = tk.Frame(
        frame_menu,
        bg=COLOR_MENU
    )

    frame_menu_superior.pack(
        fill="x"
    )

    # ============================================================
    # ÁREA CENTRAL (SUBMENÚ)
    # ============================================================

    frame_submenu = tk.Frame(
        frame_menu,
        bg=COLOR_PANEL
    )

    frame_submenu.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    # ============================================================
    # ÁREA INFERIOR (CERRAR SESIÓN)
    # ============================================================

    frame_inferior = tk.Frame(
        frame_menu,
        bg=COLOR_MENU
    )

    frame_inferior.pack(
        fill="x",
        side="bottom"
    )

    # ============================================================
    # CONTENIDO PRINCIPAL
    # ============================================================

    frame_contenido = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    frame_contenido.pack(
        side="right",
        fill="both",
        expand=True
    )

    # ============================================================
    # CABECERA
    # ============================================================

    tk.Label(
        frame_menu_superior,
        text="TECNO STORE",
        bg=COLOR_MENU,
        fg="white",
        font=("Arial", 16, "bold")
    ).pack(pady=20)

    tk.Label(
        frame_menu_superior,
        text=f"{usuario['nombre']}\n({usuario['rol']})",
        bg=COLOR_MENU,
        fg="white"
    ).pack(pady=(0, 20))

    # ============================================================
    # MENÚ PRINCIPAL
    # ============================================================

    rol = usuario["rol"]

    for menu in MENU_ROLES[rol]:

        crear_boton_menu(
            frame_menu_superior,
            menu,
            lambda m=menu: mostrar_submenu(
                frame_submenu,
                frame_contenido,
                rol,
                m,
                usuario
            )
        )

    # ============================================================
    # BOTÓN CERRAR SESIÓN
    # ============================================================

    tk.Button(
        frame_inferior,
        text="Cerrar sesión",
        command=lambda: cerrar_sesion(ventana),
        bg=COLOR_BOTON,
        fg="white"
    ).pack(
        fill="x",
        padx=10,
        pady=10
    )

    # ============================================================
    # PANTALLA INICIAL
    # ============================================================

    mostrar_dashboard(frame_contenido)

    ventana.mainloop()