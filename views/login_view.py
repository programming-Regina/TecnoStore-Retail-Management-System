"""Pantalla de ingreso de Tkinter.

La vista toma el usuario y la clave del formulario y llama directamente
a la lógica de autenticación. Esa misma función verifica los datos cuando
Flask recibe un inicio de sesión por HTTP.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from views.menu_principal import mostrar_menu_principal
from views.components import *

from logic.auth import autenticar_usuario


# PROVISORIO
from views.consultas_view import asignar_rol_logueado


# =============================================================================
# PANTALLA INICIAL -> LOGIN
# =============================================================================
def mostrar_login():

    ventana = tk.Tk()

    ventana.title("Tecno Store")
    ventana.geometry("1366x768")
    ventana.configure(bg=COLOR_FONDO)

    try:
        ventana.state("zoomed")
    except:
        pass

    contenedor = tk.Frame(
        ventana,
        bg=COLOR_PANEL,
        padx=40,
        pady=40
    )

    contenedor.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    tk.Label(
        contenedor,
        text="TECNO STORE",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO_OSCURO,
        font=("Arial", 22, "bold")
    ).pack(pady=(0, 20))

    tk.Label(
        contenedor,
        text=(
            "Usuario (NombreApellido todo junto)"
        ),
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO_OSCURO,
        justify="left",
        font=("Arial", 9)
    ).pack(pady=(0, 20))

    tk.Label(
        contenedor,
        text="Usuario",
        bg=COLOR_PANEL
    ).pack(anchor="w")

    entry_usuario = tk.Entry(contenedor, width=30)
    entry_usuario.pack(pady=(0, 15))

    tk.Label(
        contenedor,
        text="Contraseña",
        bg=COLOR_PANEL
    ).pack(anchor="w")

    entry_password = tk.Entry(
        contenedor,
        width=30,
        show="·"
    )

    entry_password.pack(pady=(0, 20))

    def validar_login():
        usuario = entry_usuario.get().strip()
        password = entry_password.get().strip()

        # Validación básica
        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor, complete todos los campos.")
            return

        # Consulta logic/auth.py pasándole el username (concatenado)
        resultado = autenticar_usuario(usuario, password)

        # Si el resultado tira "error", frena y mostramos mensaje
        if "error" in resultado:
            messagebox.showerror("Error de Autenticación", resultado["error"])
            return

        # Si loguea bien, armamos el diccionario con los datos
        usuario = {
            "nombre": resultado["nombre"],
            "rol": resultado["rol"],
            "username": resultado["username"] # Lo pasamos al menú
        }       
        
        # Setea el rol en la vista de consultas y levanta el menú principal
        asignar_rol_logueado(resultado["rol"])

        ventana.destroy()
        mostrar_menu_principal(usuario)
    

    frame_botones = tk.Frame(
    contenedor,
    bg=COLOR_PANEL
    )

    frame_botones.pack(pady=10)

    tk.Button(
        frame_botones,
        text="Ingresar",
        command=validar_login,
        bg=COLOR_BOTON,
        fg="white",
        width=15
    ).pack(side="left", padx=5)

    tk.Button(
        frame_botones,
        text="Salir",
        command=ventana.destroy,
        width=15
    ).pack(side="left", padx=5)

    # Debajo de tu botón de Login
    info_debug = "Credenciales de testeo (Usuario/Clave común: 'clave'):\n"
    info_debug += "- AdminPepe, GerentePepe\n- VendedorPepe, DepotPepe\n- VendedorJuana, VendedorRita, VendedorPipo"
    
    lbl_debug = tk.Label(contenedor, text=info_debug, fg="gray", justify=tk.LEFT, font=("Arial", 8))
    lbl_debug.pack(pady=20)

    try:
        ventana.mainloop()
    except Exception as e:
        print(f"DEBUG: El programa se cerró por: {e}")