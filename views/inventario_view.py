"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: inventario_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Pantallas de inventario del escritorio.

Para consultar el catálogo y registrar productos, Tkinter llama a la lógica
de inventario desde sus eventos. La vista muestra el resultado en una tabla
o en un mensaje. En la versión web, Flask llama a esas mismas funciones y
el navegador presenta los datos que recibe en JSON.
===============================================================================
"""

from views.components import *
from tkinter import messagebox
import tkinter as tk
from tkinter import *
from db.dao import obtener_productos_stock_critico,obtener_productos_activos_ordenados, obtener_productos_inactivos, obtener_categorias 
from logic.inventario import gestionar_baja_logica, gestionar_alta_producto, procesar_consulta_stock, gestionar_reactivacion_producto
from utils.helpers import formatear_moneda



# =============================================================================
# MOSTRAR PRODUCTOS CON STOCK BAJO
# =============================================================================
def mostrar_stock_critico(frame):
    """
    PROPÓSITO: Renderiza la pantalla para el perfil Depositero.
               Muestra los artículos que requieren reposición urgente.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Alerta de Stock Crítico")
    crear_subtitulo(frame, "Productos con menos de 5 unidades en el inventario.")

    # --- PANEL CENTRAL: TABLA DE STOCK CRÍTICO ---
    panel_datos = tk.LabelFrame(frame, text=" Requieren Reposición Inmediata ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_datos.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    columnas = ("ID", "Descripción", "Marca", "Stock Actual")
    tree_stock = ttk.Treeview(panel_datos, columns=columnas, show="headings", height=15)
    
    tree_stock.heading("ID", text="ID")
    tree_stock.column("ID", width=50, anchor=tk.CENTER)
    
    tree_stock.heading("Descripción", text="Descripción")
    tree_stock.column("Descripción", width=250, anchor=tk.W)
    
    tree_stock.heading("Marca", text="Marca")
    tree_stock.column("Marca", width=150, anchor=tk.W)
    
    # Destacamos la columna de stock
    tree_stock.heading("Stock Actual", text="Stock Actual")
    tree_stock.column("Stock Actual", width=100, anchor=tk.CENTER)
    
    tree_stock.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # =========================================================================
    # FUNCIONES INTERNAS
    # =========================================================================
    def cmd_cargar_datos():
        # Limpiar tabla de consultas anteriores
        for row in tree_stock.get_children():
            tree_stock.delete(row)
            
        # Llamar al DAO que consulta la vista SQL
        productos = obtener_productos_stock_critico()
        
        if not productos:
            tree_stock.insert("", tk.END, values=("-", "Inventario en niveles óptimos", "-", "-"))
            return
            
        for p in productos:
            tree_stock.insert("", tk.END, values=(p['id_producto'], p['descripcion'], p['marca'], p['stock']))

    # --- PANEL INFERIOR: ACCIONES ---
    frame_acciones = tk.Frame(frame, bg=COLOR_FONDO)
    frame_acciones.pack(fill=tk.X, padx=20, pady=5)
    
    tk.Button(
        frame_acciones, 
        text="🔄 Actualizar Listado", 
        bg=COLOR_BOTON, 
        fg=COLOR_TEXTO_CLARO, 
        font=("Arial", 10, "bold"),
        command=cmd_cargar_datos
    ).pack(side=tk.RIGHT)

    # ejecuta
    cmd_cargar_datos()


# =============================================================================
# CATEGORÍAS (ESTO VUELA)
# =============================================================================
def mostrar_categorias(frame):

    crear_pantalla_base(
        frame,
        "Categorías",
        "Administración y consulta de categorías de productos."
    )


# =============================================================================
# CONSULTA DE STOCK 
# =============================================================================
def mostrar_consulta_stock(frame):
    """
    PROPÓSITO: Interfaz gráfica para que el vendedor consulte rápidamente 
               el producto, su precio de venta y el stock físico disponible.
    PARÁMETROS:
        :param frame: (tk.Frame) El contenedor central de la aplicación.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)

    crear_titulo(frame, "Consulta Rápida de Stock y Precios")
    crear_subtitulo(frame, "Buscador de artículos activos en el catálogo de Tecno Store.")

    # --- PANEL SUPERIOR: BUSCADOR ---
    frame_busqueda = tk.Frame(frame, bg=COLOR_FONDO)
    frame_busqueda.pack(fill=tk.X, padx=20, pady=10)

    tk.Label(frame_busqueda, text="Nombre o Marca:", font=("Arial", 10, "bold"), bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_buscar = tk.Entry(frame_busqueda, width=35, font=("Arial", 10))
    entry_buscar.pack(side=tk.LEFT, padx=10)

    # --- PANEL CENTRAL: GRILLA DE DATOS ---
    panel_datos = tk.LabelFrame(frame, text=" Resultados de la Búsqueda ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_datos.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    columnas = ("Producto / Descripción", "Marca", "Precio al Público", "Stock Físico")
    tree = ttk.Treeview(panel_datos, columns=columnas, show="headings", height=15)

    anchos = {"Producto / Descripción": 300, "Marca": 120, "Precio al Público": 120, "Stock Físico": 100}
    
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=anchos.get(col, 100))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # =========================================================================
    # FUNCIONES INTERNAS 
    # =========================================================================
    def cargar_grilla(termino=None):
        """ Limpia la tabla y la vuelve a llenar consumiendo la capa lógica """
        for row in tree.get_children():
            tree.delete(row)
        
        # Llamada a la capa lógica
        datos = procesar_consulta_stock(termino)
        
        if not datos and termino:
            messagebox.showinfo("Sin resultados", "No se encontraron productos con ese criterio.")
            
        for d in datos:            
            tree.insert("", tk.END, values=(
                d['descripcion'],
                d['marca'],
                formatear_moneda(d['precio_venta']),
                f"{d['stock']} u."
            ))

    def cmd_buscar():
        termino = entry_buscar.get().strip()
        cargar_grilla(termino)

    def cmd_limpiar():
        entry_buscar.delete(0, tk.END)
        cargar_grilla() # Trae todo el catálogo nuevamente

    # --- BOTONES 
    tk.Button(frame_busqueda, text="🔍 Buscar", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, font=("Arial", 9, "bold"), command=cmd_buscar).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_busqueda, text="Limpiar Filtro", bg="#7f8c8d", fg=COLOR_TEXTO_CLARO, font=("Arial", 9, "bold"), command=cmd_limpiar).pack(side=tk.LEFT, padx=5)

    # Ejecución inicial para mostrar todo el catálogo apenas se abre la pantalla
    cargar_grilla()


# =============================================================================
# MOSTRAR PRODUCTOS
# =============================================================================
def mostrar_productos(frame):
    """
    PROPÓSITO: Pantalla ABM para el catálogo de productos.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Gestión de Catálogo (ABM)")
    crear_subtitulo(frame, "Alta, modificación y baja lógica de productos.")

    frame_split = tk.Frame(frame, bg=COLOR_FONDO)
    frame_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # =========================================================================
    # PANEL IZQUIERDO: FORMULARIO
    # =========================================================================
    panel_form = tk.LabelFrame(frame_split, text=" Producto Nuevo ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_form.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

    tk.Label(panel_form, text="Descripción:", bg=COLOR_FONDO).pack(anchor=tk.W, padx=10, pady=(10, 0))
    entry_desc = tk.Entry(panel_form, width=30)
    entry_desc.pack(padx=10, pady=2)

    tk.Label(panel_form, text="Marca:", bg=COLOR_FONDO).pack(anchor=tk.W, padx=10, pady=(5, 0))
    entry_marca = tk.Entry(panel_form, width=30)
    entry_marca.pack(padx=10, pady=2)

    tk.Label(panel_form, text="Último Costo $:", bg=COLOR_FONDO).pack(anchor=tk.W, padx=10, pady=(5, 0))
    entry_costo = tk.Entry(panel_form, width=30)
    entry_costo.pack(padx=10, pady=2)

    tk.Label(panel_form, text="Precio Venta $:", bg=COLOR_FONDO).pack(anchor=tk.W, padx=10, pady=(5, 0))
    entry_venta = tk.Entry(panel_form, width=30)
    entry_venta.pack(padx=10, pady=2)

    tk.Label(panel_form, text="Categoría:", bg=COLOR_FONDO).pack(anchor=tk.W, padx=10, pady=(5, 0))
    
    # Carga dinámica del desplegable
   
    categorias_bd = obtener_categorias()
    lista_cat = [f"{c['id_categoria']} - {c['categoria']}" for c in categorias_bd] if categorias_bd else ["0 - Sin categoría"]
    
    combo_cat = ttk.Combobox(panel_form, values=lista_cat, state="readonly", width=27)
    combo_cat.pack(padx=10, pady=2)
    if lista_cat:
        combo_cat.current(0)

    # Funciones de los botones
    def cmd_guardar():
        desc = entry_desc.get().strip()
        marca = entry_marca.get().strip()
        costo = entry_costo.get().strip()
        venta = entry_venta.get().strip()
        # Extrae solo el número antes del guión
        seleccion_cat = combo_cat.get()
        cat_id = seleccion_cat.split(" - ")[0] if " - " in seleccion_cat else "0"
        
        exito, msj = gestionar_alta_producto(desc, marca, costo, venta, cat_id)
        
        if exito:
            messagebox.showinfo("Éxito", msj)
            cmd_limpiar()
            mostrar_productos(frame) # Recarga la grilla
        else:
            messagebox.showerror("Error", msj)

    def cmd_eliminar():
        seleccion = tree_prod.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de retirar este producto de la venta? (Baja Lógica)"):
            item_id = int(tree_prod.item(seleccion[0])['values'][0])
            
            # Invocamos la regla de negocio
            exito, mensaje = gestionar_baja_logica(item_id)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                tree_prod.delete(seleccion[0]) # Lo quitamos de la vista
            else:
                messagebox.showerror("Error", mensaje)

    def cmd_limpiar():
        for entry in (entry_desc, entry_marca, entry_costo, entry_venta):
            entry.delete(0, tk.END)

    frame_btns = tk.Frame(panel_form, bg=COLOR_FONDO)
    frame_btns.pack(pady=20)
    
    tk.Button(frame_btns, text="💾 Guardar", bg="#27ae60", fg="white", width=12, command=cmd_guardar).grid(row=0, column=0, padx=2, pady=2)
    tk.Button(frame_btns, text="🧹 Limpiar", bg="#f39c12", fg="white", width=12, command=cmd_limpiar).grid(row=0, column=1, padx=2, pady=2)
    tk.Button(frame_btns, text="🗑️ Retirar de la venta", bg="#c0392b", fg="white", width=25, command=cmd_eliminar).grid(row=1, column=0, columnspan=2, padx=2, pady=5)

    # =========================================================================
    # PANEL DERECHO: CATÁLOGO ACTIVO
    # =========================================================================
    panel_grilla = tk.LabelFrame(frame_split, text=" Catálogo Activo ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_grilla.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

    columnas = ("ID", "Desc", "Marca", "Costo", "Venta", "Stock")
    tree_prod = ttk.Treeview(panel_grilla, columns=columnas, show="headings", height=15)
    
    tree_prod.heading("ID", text="ID")
    tree_prod.column("ID", width=40)
    for col in columnas[1:]:
        tree_prod.heading(col, text=col)
        tree_prod.column(col, width=80)
        
    tree_prod.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Cargar la grilla con db.dao.obtener_productos_activos_ordenados()    
    productos_bd = obtener_productos_activos_ordenados()
    
    for p in productos_bd:
        tree_prod.insert("", tk.END, 
                         values=(p['id_producto'], p['descripcion'], p['marca'], f"${p['precio_compra']}", f"${p['precio_venta']}", p['stock']))
        

# =============================================================================
#  MOSTRAR PRODUCTOS INACTIVOS
# =============================================================================
def mostrar_productos_inactivos(frame):
    """
    PROPÓSITO: Pantalla de productos fuera de la venta (0) o activos (1)
    """   
    
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Auditoría de Catálogo Inactivo")
    crear_subtitulo(frame, "Productos que fueron dados de baja y ya no están a la venta.")

    panel_grilla = tk.LabelFrame(frame, text=" Historial de Productos Discontinuados ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_grilla.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

    columnas = ("ID", "Desc", "Marca", "Último Costo", "Stock Remanente")
    tree_inactivos = ttk.Treeview(panel_grilla, columns=columnas, show="headings", height=15)
    
    tree_inactivos.heading("ID", text="ID")
    tree_inactivos.column("ID", width=40)
    for col in columnas[1:]:
        tree_inactivos.heading(col, text=col)
        tree_inactivos.column(col, width=120)
        
    tree_inactivos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # =========================================================================
    # FUNCIONES INTERNAS (Controladores)
    # =========================================================================
    def cargar_grilla():
        """Limpia y vuelve a llenar la grilla consumiendo la base de datos"""
        for row in tree_inactivos.get_children():
            tree_inactivos.delete(row)
            
        productos_bd = obtener_productos_inactivos()
        
        for p in productos_bd:
            tree_inactivos.insert("", tk.END, values=(
                p['id_producto'], 
                p['descripcion'], 
                p['marca'], 
                f"${p['precio_compra']}", 
                p['stock']
            ))

    def cmd_reactivar():
        """Captura el ID seleccionado, confirma y llama a la capa lógica"""
        seleccion = tree_inactivos.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla para reactivarlo.")
            return
            
        # Extrae la lista de valores de la fila
        valores = tree_inactivos.item(seleccion)['values']        
    
        id_producto = int(valores[0])
        
        respuesta = messagebox.askyesno("Confirmar Acción", f"¿Desea reincorporar el producto ID {id_producto} al catálogo de venta?")
        
        if respuesta:
            exito, mensaje = gestionar_reactivacion_producto(id_producto)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                cargar_grilla() # Recarga la tabla para que el producto desaparezca visualmente
            else:
                messagebox.showerror("Error", mensaje)

    # --- BOTÓN DE ACCIÓN INFERIOR ---
    btn_reactivar = tk.Button(
        frame, 
        text="🟢 REACTIVAR PRODUCTO SELECCIONADO", 
        bg="#27ae60", 
        fg="white", 
        font=("Arial", 11, "bold"), 
        command=cmd_reactivar
    )
    btn_reactivar.pack(pady=10)

    # Carga inicial de los datos al abrir la pantalla
    cargar_grilla()

