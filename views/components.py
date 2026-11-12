"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: components.py
CAPA: Vista (views)
DESCRIPCIÓN:
Componentes reutilizables para toda la interfaz gráfica.
La idea es evitar repetir código en cada pantalla.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# =============================================================================
# VALIDACION DE ENTRADAS NUMÉRICAS
# =============================================================================
def validar_entrada_numerica(valor):
    """
    PROPÓSITO: Valida si una entrada de texto o valor crudo puede ser convertida a un tipo flotante.
               Evita caídas de interfaz ante caracteres inválidos.


    PARÁMETROS:  
        :valor: (any) El dato ingresado por el usuario en el componente gráfico (Entry).

    RETORNO: 
        :return: (bool), True si el valor es numérico convertible a float, False en caso contrario.
    """
    try:
        float(valor)
        return True
    except ValueError:
        return False


# ============================================================================
# PALETA DE COLORES
# ============================================================================

COLOR_FONDO = "#cfe2f3"
COLOR_PANEL = "#9fc5e8"
COLOR_MENU = "#3d85c6"
COLOR_BOTON = "#0b5394"
COLOR_TEXTO_OSCURO = "#073763"
COLOR_TEXTO_CLARO = "#ffffff"

# ============================================================================
# UTILIDADES GENERALES
# ============================================================================

def limpiar_frame(frame):
    """
    Elimina todos los widgets de un Frame.

    Se usa cada vez que cambiamos de pantalla.
    """
    for widget in frame.winfo_children():
        widget.destroy()


# ============================================================================
# TÍTULOS
# ============================================================================

def crear_titulo(parent, texto):
    """
    Crea el título principal de una pantalla.
    """

    titulo = tk.Label(
        parent,
        text=texto,
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 18, "bold")
    )

    titulo.pack(anchor="w", padx=20, pady=(20, 10))

    return titulo


# =============================================================================
# SUBTÍTULOS
# =============================================================================
def crear_subtitulo(parent, texto):
    """
    Crea un subtítulo o descripción.
    """

    subtitulo = tk.Label(
        parent,
        text=texto,
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 10)
    )

    subtitulo.pack(anchor="w", padx=20)

    return subtitulo


# ============================================================================
# BOTONES
# ============================================================================

def crear_boton_menu(parent, texto, comando):
    """
    Botón principal del menú lateral.

    Ejemplo:
        Ventas
        Inventario
        Compras
    """

    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=COLOR_MENU,
        fg=COLOR_TEXTO_CLARO,
        activebackground=COLOR_BOTON,
        activeforeground=COLOR_TEXTO_CLARO,
        relief="flat",
        font=("Arial", 10, "bold"),
        width=20,
        pady=8
    )

    boton.pack(fill="x", padx=10, pady=2)

    return boton


def crear_boton_submenu(parent, texto, comando):
    """
    Botón de segundo nivel.

    Ejemplo:
        Nueva venta
        Historial ventas
    """

    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO_OSCURO,
        relief="flat",
        anchor="w",
        padx=15
    )

    boton.pack(fill="x", padx=15, pady=1)

    return boton


def crear_boton_accion(parent, texto, comando):
    """
    Botón usado dentro de las pantallas.
    """

    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=COLOR_BOTON,
        fg=COLOR_TEXTO_CLARO,
        font=("Arial", 10, "bold"),
        width=30,
        pady=6
    )

    boton.pack(pady=20)

    return boton


# ============================================================================
# CAMPOS DE ENTRADA
# ============================================================================

def crear_input(parent, texto_label):
    """
    Crea:

    Label
    Entry

    y devuelve el Entry para poder leer su valor.

    Ejemplo:

        nombre = crear_input(frame, "Nombre")
    """

    contenedor = tk.Frame(parent, bg=COLOR_FONDO)
    contenedor.pack(fill="x", padx=20, pady=5)

    label = tk.Label(
        contenedor,
        text=texto_label,
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_OSCURO,
        width=20,
        anchor="w"
    )

    label.pack(side="left")

    entry = tk.Entry(contenedor, width=40)
    entry.pack(side="left")

    return entry


# ============================================================================
# SEPARADORES
# ============================================================================

def crear_separador(parent):
    """
    Línea horizontal visual.
    """

    linea = tk.Frame(
        parent,
        bg=COLOR_TEXTO_OSCURO,
        height=1
    )

    linea.pack(fill="x", padx=15, pady=10)

    return linea


# ============================================================================
# MENSAJES PLACEHOLDER
# ============================================================================

def mostrar_funcion_correspondiente():
    """
    Placeholder temporal para el TP.

    Más adelante cada botón llamará a la lógica real.
    """

    messagebox.showinfo(
        "Tecno Store",
        "Ejecutar la función correspondiente."
    )


# ============================================================================
# PANTALLA ESTANDAR
# ============================================================================

def crear_pantalla_base(frame, titulo, descripcion):
    """
    Genera una pantalla simple para los esqueletos.

    Todas las pantallas del TP pueden reutilizar esto.
    """

    limpiar_frame(frame)

    crear_titulo(frame, titulo)

    crear_subtitulo(frame, descripcion)

    crear_boton_accion(
        frame,
        "Ejecutar función correspondiente",
        mostrar_funcion_correspondiente
    )

# ============================================================================
# COMPONENTES DE CONSULTAS Y RESULTADOS (ESTE E SEL NUEVO)
# ============================================================================

def crear_etiqueta_info(parent, texto):
    lbl = tk.Label(
        parent,
        text=texto,
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 10)
    )
    lbl.pack(pady=10)
    return lbl


def crear_etiqueta_error(parent, texto):
    """
    Crea una etiqueta de texto para mensajes de error o advertencia.
    """
    lbl = tk.Label(
        parent,
        text=texto,
        bg=COLOR_FONDO,
        fg="red",
        font=("Arial", 10, "bold")
    )
    lbl.pack(pady=20)
    return lbl


def crear_combobox(parent, valores, estado="readonly", ancho=50):
    """
    Crea un menú desplegable (Combobox) estandarizado.
    """
    combo = ttk.Combobox(
        parent,
        values=valores,
        state=estado,
        width=ancho,
        font=("Arial", 10)
    )
    combo.pack(pady=5)
    if len(valores) > 0:
        combo.current(0) # Selecciona el primero por defecto
    return combo


def crear_contenedor_resultados(parent):
    """
    Crea un frame limpio y estandarizado para mostrar resultados (tablas, textos, etc.).
    """
    frame_res = tk.Frame(
        parent,
        bg="#ffffff", # Fondo blanco para que resalten los datos
        relief="sunken",
        borderwidth=1
    )
    frame_res.pack(fill="both", expand=True, pady=15, padx=20)
    return frame_res


def mostrar_mensaje_en_resultados(frame_resultados, texto):
    """
    Limpia el frame de resultados y muestra un mensaje temporal.
    Ideal para los placeholders o mensajes de "Cargando...".
    """
    limpiar_frame(frame_resultados)
    lbl = tk.Label(
        frame_resultados,
        text=texto,
        bg="#ffffff",
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 11, "italic")
    )
    lbl.pack(expand=True) # expand=True lo centra perfectamente
    return lbl