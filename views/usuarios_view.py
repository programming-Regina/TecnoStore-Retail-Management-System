"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: usuarios_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Pantallas relacionadas con la administración de usuarios.

Estas vistas serán utilizadas exclusivamente por:
- Administrador
===============================================================================
"""

from views.components import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logic.usuarios import obtener_lista_usuarios, gestionar_alta_usuario, gestionar_modificacion_usuario, gestionar_baja_usuario, gestionar_reactivacion_usuario


# =============================================================================
# GESTIÓN DE USUARIOS
# =============================================================================

def mostrar_gestion_usuarios(frame):
    """
    PROPÓSITO: Renderiza la pantalla completa de ABM de Usuarios.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)

    crear_titulo(frame, "Gestión de Usuarios (ABM)")
    crear_subtitulo(frame, "Administración del personal, credenciales y perfiles de acceso.")

    # =========================================================================
    # LAYOUT PRINCIPAL: Paneles Izquierdo (Formulario) y Derecho (Grilla)
    # =========================================================================
    panel_izquierdo = tk.LabelFrame(frame, text=" Datos del Usuario ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)

    panel_derecho = tk.LabelFrame(frame, text=" Nómina de Personal ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=10)

    # =========================================================================
    # PANEL IZQUIERDO: FORMULARIO DE ENTRADA
    # =========================================================================
    tk.Label(panel_izquierdo, text="ID Usuario:", bg=COLOR_FONDO).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_id = tk.Entry(panel_izquierdo, state="readonly", width=10) # Solo lectura, lo maneja la BD
    entry_id.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    tk.Label(panel_izquierdo, text="Nombre:", bg=COLOR_FONDO).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_nombre = tk.Entry(panel_izquierdo, width=25)
    entry_nombre.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(panel_izquierdo, text="Apellido:", bg=COLOR_FONDO).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_apellido = tk.Entry(panel_izquierdo, width=25)
    entry_apellido.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(panel_izquierdo, text="Contraseña:", bg=COLOR_FONDO).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    entry_clave = tk.Entry(panel_izquierdo, width=25, show="·")
    entry_clave.grid(row=3, column=1, padx=10, pady=5) 

    tk.Label(panel_izquierdo, text="Rol / Perfil:", bg=COLOR_FONDO).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    # La vista presenta una lista fija de roles.
    opciones_roles = ["1 - Administrador", "2 - Gerente", "3 - Depositero", "4 - Vendedor"]
    combo_rol = ttk.Combobox(panel_izquierdo, values=opciones_roles, state="readonly", width=22)
    combo_rol.grid(row=4, column=1, padx=10, pady=5)
    combo_rol.set(opciones_roles[3]) # Por defecto Vendedor

    # =========================================================================
    # PANEL DERECHO: GRILLA Y BOTONES DE ACCIÓN
    # =========================================================================
    columnas = ("ID", "Apellido", "Nombre", "Rol", "Estado")
    tree_usuarios = ttk.Treeview(panel_derecho, columns=columnas, show="headings", height=15)
    
    # Configuramos los anchos de las columnas
    tree_usuarios.heading("ID", text="ID")
    tree_usuarios.column("ID", width=40, anchor="center")
    tree_usuarios.heading("Apellido", text="Apellido")
    tree_usuarios.column("Apellido", width=120)
    tree_usuarios.heading("Nombre", text="Nombre")
    tree_usuarios.column("Nombre", width=120)
    tree_usuarios.heading("Rol", text="Rol")
    tree_usuarios.column("Rol", width=100)
    tree_usuarios.heading("Estado", text="Estado")
    tree_usuarios.column("Estado", width=80, anchor="center")

    tree_usuarios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Frame interno para los botones debajo de la grilla
    frame_botones_grilla = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_botones_grilla.pack(fill=tk.X, padx=10, pady=5)

    # =========================================================================
    # FUNCIONES CONTROLADORAS DE LA VISTA
    # =========================================================================
    def cargar_grilla():
        """Limpia y repuebla la tabla de usuarios."""
        for row in tree_usuarios.get_children():
            tree_usuarios.delete(row)
        
        usuarios_bd = obtener_lista_usuarios()
        for u in usuarios_bd:
            estado_txt = "Activo" if u['activo'] == 1 else "Inactivo"
            tree_usuarios.insert("", tk.END, values=(
                u['id_usuario'], u['apellido'], u['nombre'], u['nombre_rol'], estado_txt
            ))

    def limpiar_formulario():
        """Blanquea los inputs para preparar un alta nueva."""
        entry_id.config(state=tk.NORMAL)
        entry_id.delete(0, tk.END)
        entry_id.config(state="readonly")
        
        entry_nombre.delete(0, tk.END)
        entry_apellido.delete(0, tk.END)
        entry_clave.delete(0, tk.END)
        combo_rol.set(opciones_roles[3])

    def seleccionar_registro(event=None):
        """Pasa los datos de la grilla al formulario al hacer clic."""
        seleccion = tree_usuarios.selection()
        if not seleccion:
            return
            
        valores = tree_usuarios.item(seleccion)['values']
        limpiar_formulario()
        
        # Llenamos el ID
        entry_id.config(state=tk.NORMAL)
        entry_id.insert(0, valores[0])
        entry_id.config(state="readonly")
        
        # Llenamos el resto
        entry_apellido.insert(0, valores[1])
        entry_nombre.insert(0, valores[2])
        # La clave por seguridad no la traemos de la grilla, el admin la sobrescribe si quiere
        
        # Mapeamos el nombre del rol al combo
        nombre_rol_grilla = valores[3]
        for opt in opciones_roles:
            if nombre_rol_grilla in opt:
                combo_rol.set(opt)
                break

    # Bindeamos el evento de clic en la grilla
    tree_usuarios.bind("<<TreeviewSelect>>", seleccionar_registro)

    def cmd_guardar():
        """Toma la decisión de si es un Alta (ID vacío) o una Modificación (ID lleno)."""
        id_actual = entry_id.get()
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        clave = entry_clave.get()
        
        # Truco: "1 - Administrador".split("-")[0].strip() -> "1"
        id_rol_seleccionado = combo_rol.get().split("-")[0].strip() 

        if id_actual == "":
            # ALTA
            exito, mensaje = gestionar_alta_usuario(apellido, nombre, clave, id_rol_seleccionado)
        else:
            # MODIFICACIÓN
            exito, mensaje = gestionar_modificacion_usuario(id_actual, apellido, nombre, clave, id_rol_seleccionado)
            
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            cargar_grilla()
            limpiar_formulario()
        else:
            messagebox.showerror("Error", mensaje)

    def cmd_baja():
        """Baja lógica del usuario seleccionado."""
        seleccion = tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un usuario para dar de baja.")
            return
            
        id_user = tree_usuarios.item(seleccion)['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Dar de baja al usuario ID {id_user}?"):
            exito, msg = gestionar_baja_usuario(id_user)
            if exito:
                messagebox.showinfo("Éxito", msg)
                cargar_grilla()
                limpiar_formulario()
            else:
                messagebox.showerror("Error", msg)

    def cmd_reactivar():
        """Reactivación del usuario seleccionado."""
        seleccion = tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un usuario inactivo para reactivar.")
            return
            
        id_user = tree_usuarios.item(seleccion)['values'][0]
        exito, msg = gestionar_reactivacion_usuario(id_user)
        if exito:
            messagebox.showinfo("Éxito", msg)
            cargar_grilla()
        else:
            messagebox.showerror("Error", msg)

    # =========================================================================
    # RENDERIZADO DE BOTONES
    # =========================================================================
    # Botones del Formulario (Izquierda)
    tk.Button(panel_izquierdo, text="💾 GUARDAR", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, font=("Arial", 10, "bold"), command=cmd_guardar).grid(row=5, column=0, columnspan=2, pady=15, sticky="ew", padx=10)
    tk.Button(panel_izquierdo, text="🧹 Limpiar Campos", command=limpiar_formulario).grid(row=6, column=0, columnspan=2, sticky="ew", padx=10)

    # Botones de la Grilla (Derecha)
    tk.Button(frame_botones_grilla, text="🔴 Dar de Baja", bg="#c0392b", fg="white", font=("Arial", 9, "bold"), command=cmd_baja).pack(side=tk.RIGHT, padx=5)
    tk.Button(frame_botones_grilla, text="🟢 Reactivar", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), command=cmd_reactivar).pack(side=tk.RIGHT, padx=5)

    # Inicialización
    cargar_grilla()