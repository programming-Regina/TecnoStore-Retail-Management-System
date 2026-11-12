"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: ventas_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Contiene las interfaces gráficas y controladores de eventos para el Punto de 
Venta (POS), Historial de Facturación, Anulaciones y Auditoría Diaria.
Alineado con el estándar transaccional y validación de doble capa.

===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.components import limpiar_frame, validar_entrada_numerica, crear_titulo, crear_subtitulo, COLOR_FONDO,  COLOR_BOTON,  COLOR_TEXTO_CLARO, crear_contenedor_resultados
from logic.ventas import calcular_subtotal_memoria, registrar_venta_transaccion, procesar_historial_ventas, procesar_detalle_venta, anular_venta_transaccion, obtener_detalle_para_anulacion
from db.dao import buscar_productos_por_nombre, obtener_historial_ventas, obtener_formas_pago
from utils.ticket import generar_ticket, formatear_moneda
import logic.auth as auth

# =============================================================================
# NUEVA VENTA (PUNTO DE VENTA - POS)
# =============================================================================
def mostrar_nueva_venta(frame):
    """
    PROPÓSITO: Renderiza el Punto de Venta (POS). Maneja el ciclo de búsqueda de productos, 
               armado del carrito en memoria y envío de la transacción a la base de datos.


    PARÁMETROS:  
        :frame: (tk.Frame) El contenedor principal donde se dibujará la pantalla.        
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)

    # Variable de estado temporal en memoria (no tenemos POO)
    carrito_actual = [] 

    mapa_formas_pago = obtener_formas_pago()
    nombres_formas_pago = list(mapa_formas_pago.keys())

    # =========================================================================
    # FUNCIONES INTERNAS (Controladores de Eventos)
    # =========================================================================
    
    def mostrar_popup_ticket_visual(texto_comprobante):
        """
        PROPÓSITO: Construye una ventana emergente modal que emula la impresión 
                   de un comprobante fiscal en papel térmico con fuentes monoespaciadas.
        """
        ventana_ticket = tk.Toplevel()
        ventana_ticket.title("Comprobante de Venta - Emisión POS")
        ventana_ticket.geometry("380x520")
        ventana_ticket.configure(bg="#ffffff")
        ventana_ticket.resizable(False, False)
        
        # Bloquea la ventana padre de fondo hasta cerrar el popup 
        ventana_ticket.grab_set()

        txt_area = tk.Text(ventana_ticket, font=("Courier New", 10), bd=0, padx=15, pady=15)
        txt_area.insert(tk.END, texto_comprobante)
        txt_area.config(state="disabled") # Bloquea manipulación
        txt_area.pack(fill=tk.BOTH, expand=True)

        btn_cerrar = tk.Button(
            ventana_ticket, 
            text="Cerrar e Imprimir", 
            bg=COLOR_BOTON, 
            fg=COLOR_TEXTO_CLARO, 
            font=("Arial", 10, "bold"),
            command=ventana_ticket.destroy
        )
        btn_cerrar.pack(fill=tk.X, padx=20, pady=10)

    def cmd_buscar():
        termino = entry_buscar.get().strip()
        if not termino:
            messagebox.showwarning("Atención", "Ingrese un producto a buscar.")
            return
            
        resultados = buscar_productos_por_nombre(termino)
        
        # Limpiar grilla izquierda
        for row in tree_resultados.get_children():
            tree_resultados.delete(row)
            
        # Llenar grilla izquierda
        for prod in resultados:
            tree_resultados.insert("", tk.END, text=prod['id_producto'], 
                                   values=(prod['descripcion'], prod['marca'], f"${prod['precio_venta']}", prod['stock']))

    def cmd_agregar_carrito():
        seleccion = tree_resultados.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla de resultados.")
            return
            
        cantidad_txt = entry_cantidad.get()
        if not validar_entrada_numerica(cantidad_txt) or int(cantidad_txt) <= 0:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a cero.")
            return
            
        cantidad = int(cantidad_txt)
        item_id = tree_resultados.item(seleccion[0])['text']
        valores = tree_resultados.item(seleccion[0])['values'] 
        
        precio_float = float(valores[2].replace("$", ""))
        stock_disponible = int(valores[3])
        
        if cantidad > stock_disponible:
            messagebox.showerror("Stock Insuficiente", f"Solo hay {stock_disponible} unidades disponibles.")
            return
            
        # 1. Agregar a la lista lógica
        nuevo_item = {
            'id_producto': item_id,
            'descripcion': valores[0],
            'cantidad': cantidad,
            'precio_unitario': precio_float
        }
        carrito_actual.append(nuevo_item)
        
        # 2. Reflejar en la grilla visual derecha
        subtotal = cantidad * precio_float
        tree_carrito.insert("", tk.END, values=(valores[0], cantidad, f"${precio_float:.2f}", f"${subtotal:.2f}"))
        
        # 3. Actualizar etiqueta de Totales
        actualizar_total_gui()

    def actualizar_total_gui():
        total = calcular_subtotal_memoria(carrito_actual)
        lbl_subtotal.config(text=f"Subtotal: {formatear_moneda(total)}")
        lbl_iva.config(text=f"IVA (21%): {formatear_moneda(total * 0.21)}")
        lbl_total.config(text=f"Total: {formatear_moneda(total * 1.21)}")
        

    def cmd_confirmar_venta():
        if not carrito_actual:
            messagebox.showwarning("Carrito Vacío", "No hay productos para vender.")
            return
            
        # formas_pago_map = {"Efectivo": 1, "Tarjeta de Débito": 2, "Tarjeta de Crédito": 3, etc}
        seleccion_pago = combo_pago.get()
        id_forma_pago = mapa_formas_pago.get(seleccion_pago, 1)

        total_venta = calcular_subtotal_memoria(carrito_actual)

        id_factura = registrar_venta_transaccion(id_forma_pago, auth.USUARIO_ID, carrito_actual)
        
        if id_factura:
            datos_bd = obtener_detalle_para_anulacion(id_factura)
            nombre_vendedor = datos_bd['cabecera']['vendedor'] if datos_bd else "N/A"
            texto_ticket_final = generar_ticket(carrito_actual, total_venta, nombre_vendedor, id_venta=id_factura)
            mostrar_popup_ticket_visual(texto_ticket_final)
            
            messagebox.showinfo("Éxito", f"Venta registrada. Factura N° {id_factura}")
            mostrar_nueva_venta(frame) 
        else:
            messagebox.showerror("Error", "Ocurrió un problema en la transacción. Operación abortada.")


    # =========================================================================
    # MAQUETACIÓN 
    # =========================================================================
    crear_titulo(frame, "PUNTO DE VENTA (POS)")

    # tk.Label(frame, text="PUNTO DE VENTA (POS)", font=("Arial", 16, "bold"), bg=COLOR_FONDO).pack(pady=10)

    frame_split = tk.Frame(frame, bg=COLOR_FONDO)
    frame_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # --- PANEL IZQUIERDO ---
    panel_izq = tk.LabelFrame(frame_split, text="1. Buscar Productos", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    frame_busqueda = tk.Frame(panel_izq, bg=COLOR_FONDO)
    frame_busqueda.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(frame_busqueda, text="Nombre/Marca:", bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_buscar = tk.Entry(frame_busqueda, width=30)
    entry_buscar.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_busqueda, text="🔍 Buscar", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, command=cmd_buscar).pack(side=tk.LEFT)

    columnas_res = ("Desc", "Marca", "Precio", "Stock")
    tree_resultados = ttk.Treeview(panel_izq, columns=columnas_res, show="headings", height=8)
    for col in columnas_res:
        tree_resultados.heading(col, text=col)
        tree_resultados.column(col, width=80)
    tree_resultados.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    frame_agregar = tk.Frame(panel_izq, bg=COLOR_FONDO)
    frame_agregar.pack(fill=tk.X, padx=5, pady=10)
    tk.Label(frame_agregar, text="Cantidad:", bg=COLOR_FONDO).pack(side=tk.LEFT)
    entry_cantidad = tk.Entry(frame_agregar, width=10)
    entry_cantidad.insert(0, "1") 
    entry_cantidad.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_agregar, text=" Agregar al Carrito ➔", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=cmd_agregar_carrito).pack(side=tk.RIGHT)

    # --- PANEL DERECHO ---
    panel_der = tk.LabelFrame(frame_split, text="2. Carrito de Compras", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    columnas_cart = ("Desc", "Cant", "P.Unit", "Subtotal")
    tree_carrito = ttk.Treeview(panel_der, columns=columnas_cart, show="headings", height=8)
    for col in columnas_cart:
        tree_carrito.heading(col, text=col)
        tree_carrito.column(col, width=80)
    tree_carrito.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# --- Modificación en el Panel Derecho ---
    frame_cobro = tk.Frame(panel_der, bg=COLOR_FONDO)
    frame_cobro.pack(fill=tk.X, padx=5, pady=10)

    # Contenedor para forma de pago a la izquierda
    frame_pago_izq = tk.Frame(frame_cobro, bg=COLOR_FONDO)
    frame_pago_izq.pack(side=tk.LEFT, fill=tk.Y)
    
    tk.Label(frame_pago_izq, text="Forma de Pago:", bg=COLOR_FONDO).pack(anchor="w")
    combo_pago = ttk.Combobox(frame_pago_izq, values=nombres_formas_pago, state="readonly", width=25)
    combo_pago.current(0)
    combo_pago.pack(anchor="w", pady=5)

    # Contenedor de totales a la derecha (aquí apilamos verticalmente)
    frame_totales_der = tk.Frame(frame_cobro, bg=COLOR_FONDO)
    frame_totales_der.pack(side=tk.RIGHT, fill=tk.Y)

    # Se apilan usando pack() sin especificar 'side', por defecto se apilan verticalmente
    lbl_subtotal = tk.Label(frame_totales_der, text="Subtotal: $0.00", bg=COLOR_FONDO, font=("Arial", 10, "bold"), anchor="e")
    lbl_subtotal.pack(anchor="e", pady=2)
    
    lbl_iva = tk.Label(frame_totales_der, text="IVA (21%): $0.00", bg=COLOR_FONDO, font=("Arial", 10, "bold"), anchor="e")
    lbl_iva.pack(anchor="e", pady=2)
    
    lbl_total = tk.Label(frame_totales_der, text="TOTAL: $0.00", bg=COLOR_FONDO, font=("Arial", 10, "bold"), fg="#c0392b", anchor="e")
    lbl_total.pack(anchor="e", pady=2)


    tk.Button(panel_der, text="💳 CONFIRMAR Y EMITIR TICKET", bg="#2980b9", fg="white", font=("Arial", 12, "bold"), command=cmd_confirmar_venta).pack(fill=tk.X, padx=20, pady=10)


# =============================================================================
# HISTORIAL DE VENTAS
# =============================================================================
def mostrar_historial_ventas(frame):
    """
    PROPÓSITO: Renderiza el historial general de operaciones de la tienda.
    Valida la selección obligatoria antes de derivar flujos de gestión.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Historial de Ventas")
    crear_subtitulo(frame, "Seleccione una factura de la lista para auditar sus detalles o solicitar una baja.")

    # Contenedor para la tabla de registros
    frame_tabla = tk.Frame(frame, bg=COLOR_FONDO)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("id_venta", "fecha", "vendedor", "total")
    tree_historial = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)
    
    tree_historial.heading("id_venta", text="N° Factura")
    tree_historial.heading("fecha", text="Fecha / Hora")
    tree_historial.heading("vendedor", text="Personal de Venta")
    tree_historial.heading("total", text="Monto Total")

    tree_historial.column("id_venta", width=120, anchor="center")
    tree_historial.column("fecha", width=180, anchor="center")
    tree_historial.column("vendedor", width=280, anchor="w")
    tree_historial.column("total", width=150, anchor="e")
    
    tree_historial.pack(fill="both", expand=True, side="left")
    
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree_historial.yview)
    tree_historial.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # LLenar la grilla 
    ventas = obtener_historial_ventas()
    for v in ventas:
        vendedor_nombre = f"{v.get('nombre', '')} {v.get('apellido', '')}".strip()
        total_pesos = formatear_moneda(v.get('total', 0))
        tree_historial.insert("", "end", values=(v.get('id_venta'), v.get('fecha'), vendedor_nombre, total_pesos))

    # --- Controladores de eventos internos ---
    def procesar_seleccion_mostrar(): 
        seleccion = tree_historial.selection()
        if not seleccion:
            messagebox.showwarning("Selección Requerida", "Debe seleccionar una operación del listado antes de presionar Mostrar.")
            return
            
        # Extraemos datos
        valores = tree_historial.item(seleccion[0])['values']
        id_venta = valores[0]
        vendedor_nombre = valores[2]
        
        # Obtenemos el diccionario con 'cabecera' y 'detalles'
        datos_completos = obtener_detalle_para_anulacion(id_venta)
        
        if datos_completos and datos_completos.get("detalles"):
            detalles = datos_completos["detalles"]
            print (datos_completos["detalles"])
            # Sumamos los subtotales para obtener el total del ticket
            total_final = sum(float(item.get('subtotal', 0)) for item in detalles) # A VEEEEEEEEEEEEEEEERRRRR?
            
            # Generamos el ticket reutilizando la utilidad existente
            texto_ticket = generar_ticket(detalles, total_final, vendedor_nombre=vendedor_nombre, id_venta=id_venta)
            
            # Reutilizamos la ventana que muestra el ticket.
            ventana_ticket = tk.Toplevel()
            ventana_ticket.title(f"Comprobante - Factura N° {id_venta}")
            ventana_ticket.geometry("380x520")
            ventana_ticket.configure(bg="#ffffff")
            ventana_ticket.grab_set()
            
            txt_area = tk.Text(ventana_ticket, font=("Courier New", 10), bd=0, padx=15, pady=15)
            txt_area.insert(tk.END, texto_ticket)
            txt_area.config(state="disabled")
            txt_area.pack(fill=tk.BOTH, expand=True)
            
            tk.Button(ventana_ticket, text="Cerrar", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, command=ventana_ticket.destroy).pack(fill=tk.X, padx=20, pady=10)
            
        else:
            messagebox.showerror("Error", "No se pudo recuperar el detalle de la operación.")

    def procesar_seleccion_anular():
        # Verificación explícita de selección obligatoria solicitada
        seleccion = tree_historial.selection()
        if not seleccion:
            messagebox.showwarning("Selección Requerida", "Debe seleccionar una operación del listado antes de presionar Anular.")
            return
            
        valores = tree_historial.item(seleccion[0])['values']
        id_venta = valores[0]
        
        # Redirección automática 
        mostrar_anular_venta(frame, id_venta_predefinido=id_venta)

    # Panel inferior de interacción
    frame_botones = tk.Frame(frame, bg=COLOR_FONDO)
    frame_botones.pack(pady=20)

    btn_mostrar = tk.Button(frame_botones, text="Mostrar Detalle", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, font=("Arial", 11, "bold"), width=18, command=procesar_seleccion_mostrar)
    btn_mostrar.pack(side="left", padx=15)

    btn_anular = tk.Button(frame_botones, text="Anular Operación", bg="#cc0000", fg=COLOR_TEXTO_CLARO, font=("Arial", 11, "bold"), width=18, command=procesar_seleccion_anular)
    btn_anular.pack(side="left", padx=15)


# =============================================================================
# ANULACIÓN DE VENTA
# =============================================================================
def mostrar_anular_venta(frame, id_venta_predefinido=None):
    """
    PROPÓSITO: Interfaz gráfica de reversión de operaciones de caja.
    Soporta la precarga y ejecución automatizada cuando proviene del historial.
    """
    limpiar_frame(frame)
    frame.config(bg=COLOR_FONDO)
    
    crear_titulo(frame, "Anulación de Comprobantes")
    crear_subtitulo(frame, "Inspeccione los artículos vinculados a la transacción antes de confirmar su revocación.")

    # Panel de Búsqueda Manual / Control
    frame_busqueda = tk.Frame(frame, bg=COLOR_FONDO)
    frame_busqueda.pack(pady=10)

    tk.Label(frame_busqueda, text="N° Factura:", bg=COLOR_FONDO, font=("Arial", 11, "bold")).pack(side="left", padx=5)
    entry_id_venta = tk.Entry(frame_busqueda, font=("Arial", 11), width=15)
    entry_id_venta.pack(side="left", padx=5)

    # Panel contenedor de datos (panel_datos solicitado)
    panel_datos = tk.LabelFrame(frame, text=" Desglose de Artículos Registrados ", bg=COLOR_FONDO, font=("Arial", 10, "bold"))
    panel_datos.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("descripcion", "marca", "cantidad", "precio", "subtotal")
    tree_detalle = ttk.Treeview(panel_datos, columns=columnas, show="headings", height=10)
    
    tree_detalle.heading("descripcion", text="Descripción del Producto")
    tree_detalle.heading("marca", text="Marca")
    tree_detalle.heading("cantidad", text="Cant.")
    tree_detalle.heading("precio", text="P. Unitario")
    tree_detalle.heading("subtotal", text="Subtotal Item")
    
    tree_detalle.column("descripcion", width=300, anchor="w")
    tree_detalle.column("marca", width=120, anchor="center")
    tree_detalle.column("cantidad", width=70, anchor="center")
    tree_detalle.column("precio", width=120, anchor="e")
    tree_detalle.column("subtotal", width=120, anchor="e")
    tree_detalle.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Métodos internos 
    def ejecutar_busqueda_especifica():
        # limpia  panel de datos
        for item in tree_detalle.get_children():
            tree_detalle.delete(item)
            
        factura_id = entry_id_venta.get().strip()
        if not factura_id.isdigit():
            messagebox.showwarning("Entrada Inválida", "Por favor, especifique un número de factura estrictamente numérico.")
            return

        #  dict {"cabecera": {...}, "detalles": [...]}
        datos_venta = obtener_detalle_para_anulacion(int(factura_id))
        
        # que traiga detalles
        if not datos_venta or not datos_venta.get("detalles"):
            messagebox.showinfo("Búsqueda", f"No se encontraron registros asociados al comprobante N° {factura_id}.")
            return
            
        # aisla artículos
        detalles_factura = datos_venta["detalles"]
        
        for fila in detalles_factura:
            desc = fila.get('descripcion', 'Desconocido')
            marca = fila.get('marca', 'N/A')
            cant = fila.get('cantidad', 0)
            precio = fila.get('precio_unitario', 0)
            subtotal = fila.get('subtotal', 0) # El subtotal ya viene calculado 
            
            tree_detalle.insert("", "end", values=(
                desc,
                marca,
                cant,
                formatear_moneda(precio),
                formatear_moneda(subtotal)
            ))


    def confirmar_reversion_total():
        factura_id = entry_id_venta.get().strip()
        if not factura_id.isdigit() or not tree_detalle.get_children():
            messagebox.showwarning("Operación Requerida", "Debe cargar una factura válida con artículos en el panel antes de confirmar.")
            return
            
        seguridad = messagebox.askyesno("Reversión Crítica de Stock", 
                                        f"¿Confirma la anulación atómica de la factura N° {factura_id}?\n\nEsta acción eliminará los registros de venta y repondrá las cantidades en el inventario.")
        if seguridad:
            try:
                anular_venta_transaccion(int(factura_id))
                messagebox.showinfo("Éxito", f"La factura N° {factura_id} fue eliminada. El inventario se ha actualizado.")
                mostrar_historial_ventas(frame)
            except Exception as e:
                messagebox.showerror("Fallo de Transacción", f"Error crítico al revertir la operación en la base de datos: {e}")

    # Montaje de controles interactivos en la vista
    btn_buscar = tk.Button(frame_busqueda, text="🔍 Buscar Factura", bg=COLOR_BOTON, fg=COLOR_TEXTO_CLARO, font=("Arial", 10, "bold"), command=ejecutar_busqueda_especifica)
    btn_buscar.pack(side="left", padx=10)

    btn_confirmar = tk.Button(frame, text="Confirmar Anulación", bg="#cc0000", fg=COLOR_TEXTO_CLARO, font=("Arial", 11, "bold"), width=25, command=confirmar_reversion_total)
    btn_confirmar.pack(pady=15)

    # --- AUTOMATIZACIÓN DE FLUJO DESDE HISTORIAL ---
    # Si la función detecta que recibió un ID, lo escribe en el Entry
    # y rellena el panel
    if id_venta_predefinido is not None:
        entry_id_venta.delete(0, tk.END)
        entry_id_venta.insert(0, str(id_venta_predefinido))
        ejecutar_busqueda_especifica()


