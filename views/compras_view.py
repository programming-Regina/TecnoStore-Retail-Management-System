"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: compras_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Pantallas relacionadas con compras y proveedores.

Estas vistas serán utilizadas principalmente por:
- Administrador
- Depositero
===============================================================================
"""

from views.components import *
import tkinter as tk
from tkinter import ttk, messagebox
from db.dao import buscar_productos_por_nombre, registrar_compra_transaccion, listar_proveedores_activos


# =============================================================================
# REGISTRAR COMPRA
# =============================================================================
def mostrar_registrar_compra(frame, id_usuario_logueado=1):
    """
    PROPÓSITO: Renderiza la pantalla de compras. Maneja la selección dinámica del proveedor,
               el armado de la orden en memoria y la persistencia transaccional.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Ingreso de Mercadería (Compras)")
    crear_subtitulo(frame, "Registre la entrada de stock copiando el costo unitario desde la factura del proveedor.")

    # El changuito
    orden_actual = []

    # =========================================================================
    # CARGA DE DATOS (Memoricen!! Capa Datos -> Interfaz) 
    # =========================================================================
    proveedores_bd = listar_proveedores_activos()
    
    if proveedores_bd:
        # Usamos razon_social 
        lista_prov_combo = [f"{p['id_proveedor']} - {p['razon_social']}" for p in proveedores_bd]
    else:
        lista_prov_combo = ["0 - Sin proveedores activos"]

    # =========================================================================
    # FUNCIONES INTERNAS 
    # =========================================================================
    
    def cmd_buscar():
        termino = entry_buscar.get().strip()
        if not termino:
            messagebox.showwarning("Atención", "Ingrese un producto a buscar.")
            return
            
        resultados = buscar_productos_por_nombre(termino)
        
        for row in tree_resultados.get_children():
            tree_resultados.delete(row)
            
        for prod in resultados:
            # La persona que registra la compra ingresa el costo de forma manual.
            tree_resultados.insert("", tk.END, text=prod['id_producto'], 
                                   values=(prod['descripcion'], prod['marca'], "-", prod['stock']))

    def cmd_seleccionar_producto(event):
        """ Al hacer clic en un producto, limpia la caja de costo para forzar el ingreso del nuevo valor """
        seleccion = tree_resultados.selection()
        if seleccion:
            entry_costo.delete(0, tk.END)
            entry_costo.insert(0, "") # aca ponen el precio

    def cmd_agregar_orden():
        seleccion = tree_resultados.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla de resultados.")
            return
            
        cant_txt = entry_cantidad.get()
        costo_txt = entry_costo.get()
        
        if not validar_entrada_numerica(cant_txt) or int(cant_txt) <= 0:
            messagebox.showerror("Error", "La cantidad debe ser un entero mayor a cero.")
            return
            
        if not validar_entrada_numerica(costo_txt) or float(costo_txt) <= 0:
            messagebox.showerror("Error", "El costo unitario debe ser un número válido mayor a cero.")
            return
            
        cantidad = int(cant_txt)
        costo_unitario = float(costo_txt)
        item_id = tree_resultados.item(seleccion[0])['text']
        valores = tree_resultados.item(seleccion[0])['values'] 
        
        nuevo_item = {
            'id_producto': item_id,
            'descripcion': valores[0],
            'cantidad': cantidad,
            'precio_costo': costo_unitario
        }
        orden_actual.append(nuevo_item)
        
        subtotal = cantidad * costo_unitario
        tree_orden.insert("", tk.END, values=(valores[0], cantidad, f"${costo_unitario:.2f}", f"${subtotal:.2f}"))
        actualizar_total_gui()

    def actualizar_total_gui():
        total = sum((item['cantidad'] * item['precio_costo']) for item in orden_actual)
        lbl_total.config(text=f"TOTAL INVERSIÓN: ${total:.2f}")

    def cmd_confirmar_compra():
        if not orden_actual:
            messagebox.showwarning("Orden Vacía", "No hay productos para ingresar.")
            return
            
        seleccion_prov = combo_proveedor.get()
        
        # Extracción del ID 
        try:
            id_proveedor = int(seleccion_prov.split(" - ")[0])
            if id_proveedor == 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de Datos", "Selección de proveedor inválida. Registre un proveedor primero.")
            return

        # Invocamos la transacción 
        exito = registrar_compra_transaccion(id_proveedor, orden_actual)
        
        if exito:
            messagebox.showinfo("Éxito", "Ingreso registrado. El stock ha sido actualizado.")
            mostrar_registrar_compra(frame, id_usuario_logueado) # Recarga limpia
        else:
            messagebox.showerror("Error", "Ocurrió un problema transaccional al registrar la compra.")

    # =========================================================================
    # MAQUETACIÓN VISUAL
    # =========================================================================
    
    # --- PROVEEDOR ---
    frame_prov = tk.Frame(frame, bg=COLOR_FONDO)
    frame_prov.pack(fill=tk.X, padx=20, pady=5)
    tk.Label(frame_prov, text="Proveedor:", bg=COLOR_FONDO, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    # Inyectamos la lista de la BD
    combo_proveedor = ttk.Combobox(frame_prov, values=lista_prov_combo, state="readonly", width=40)
    combo_proveedor.current(0)
    combo_proveedor.pack(side=tk.LEFT, padx=10)

    frame_split = tk.Frame(frame, bg=COLOR_FONDO)
    frame_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # --- PANEL IZQUIERDO: BÚSQUEDA ---
    panel_izq = tk.LabelFrame(frame_split, text="1. Buscar Producto a Ingresar", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    frame_busqueda = tk.Frame(panel_izq, bg=COLOR_FONDO)
    frame_busqueda.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(frame_busqueda, text="Nombre/Marca:", bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_buscar = tk.Entry(frame_busqueda, width=20)
    entry_buscar.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_busqueda, text="🔍 Buscar", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, command=cmd_buscar).pack(side=tk.LEFT)

    # CORRECCIÓN DE UX: Cambiamos nombre de la columna a "Costo Factura"
    columnas_res = ("Desc", "Marca", "Costo Factura", "Stock Act.")
    tree_resultados = ttk.Treeview(panel_izq, columns=columnas_res, show="headings", height=6)
    for col in columnas_res:
        tree_resultados.heading(col, text=col)
        tree_resultados.column(col, width=70)
    tree_resultados.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    tree_resultados.bind("<<TreeviewSelect>>", cmd_seleccionar_producto)

    frame_agregar = tk.Frame(panel_izq, bg=COLOR_FONDO)
    frame_agregar.pack(fill=tk.X, padx=5, pady=10)
    
    tk.Label(frame_agregar, text="Cant:", bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_cantidad = tk.Entry(frame_agregar, width=5)
    entry_cantidad.pack(side=tk.LEFT, padx=5)
    
    tk.Label(frame_agregar, text="Costo Unit. $:", bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_costo = tk.Entry(frame_agregar, width=10)
    entry_costo.pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_agregar, text="Agregar a Orden ➔", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=cmd_agregar_orden).pack(side=tk.RIGHT)

    # --- PANEL DERECHO: ORDEN DE COMPRA ---
    panel_der = tk.LabelFrame(frame_split, text="2. Orden de Compra Actual", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    columnas_ord = ("Desc", "Cant", "Costo Un.", "Subtotal")
    tree_orden = ttk.Treeview(panel_der, columns=columnas_ord, show="headings", height=8)
    for col in columnas_ord:
        tree_orden.heading(col, text=col)
        tree_orden.column(col, width=70)
    tree_orden.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    lbl_total = tk.Label(panel_der, text="TOTAL INVERSIÓN: $0.00", bg=COLOR_FONDO, font=("Arial", 14, "bold"), fg="#c0392b")
    lbl_total.pack(side=tk.RIGHT, pady=5, padx=10)

    tk.Button(frame, text="📦 CONFIRMAR INGRESO DE MERCADERÍA", bg="#8e44ad", fg="white", font=("Arial", 12, "bold"), command=cmd_confirmar_compra).pack(fill=tk.X, padx=20, pady=15)


# =============================================================================
# PROVEEDORES (VEREMOS)
# =============================================================================

def mostrar_proveedores(frame):

    crear_pantalla_base(
        frame,
        "Proveedores",
        "Administración y consulta de proveedores."
    )