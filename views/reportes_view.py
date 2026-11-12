"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: reportes_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Pantallas relacionadas con reportes y análisis.
Estas vistas serán utilizadas principalmente por Administrador y Gerente.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk

from views.components import limpiar_frame, crear_titulo, crear_subtitulo, COLOR_FONDO
from utils.helpers import formatear_moneda
from logic.reportes import  procesar_rendimiento_vendedores, procesar_ranking_productos, procesar_mis_ventas, procesar_rendimientos_mensuales, procesar_ventas_por_forma_pago

# =============================================================================
# RENDIMIENTO POR VENDEDOR (GERENCIA)
# =============================================================================
def mostrar_rendimiento_vendedor(frame):
    limpiar_frame(frame)
    crear_titulo(frame, "Rendimiento por Vendedor")
    crear_subtitulo(frame, "Análisis mensual de ventas, costos operativos y margen de ganancia neto.")

    columnas = ("Mes", "Vendedor", "Total Vendido", "Costo Mercadería", "Margen de Ganancia")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=15)
    
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

    datos_rendimiento = procesar_rendimiento_vendedores()
    
    for fila in datos_rendimiento:
        tree.insert("", tk.END, values=(
            fila['mes'],
            fila['vendedor'],
            formatear_moneda(fila['total_vendido']),   
            formatear_moneda(fila['costo_total']),     
            formatear_moneda(fila['margen_ganancia'])
        ))


# =============================================================================
# MIS VENTAS (VENDEDOR)
# =============================================================================
def mostrar_mis_ventas(frame, usuario_logueado):        
    limpiar_frame(frame)
    crear_titulo(frame, f"Historial de Ventas: {usuario_logueado['nombre']}")
    crear_subtitulo(frame, "Listado de tus operaciones registradas por mes.")

    columnas = ("Fecha", "Monto Total")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=15)
    
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

    historial = procesar_mis_ventas(usuario_logueado['nombre'])
    
    total_acumulado = 0
    for h in historial:
        tree.insert("", tk.END, values=(
            h['mes_anio'],
            formatear_moneda(h['total_mes']) # Usamos el helper acá también
        ))
        total_acumulado += float(h['total_mes'])
    
    lbl_total = tk.Label(frame, text=f"TOTAL ACUMULADO VENDIDO: {formatear_moneda(total_acumulado)}", 
                         font=("Arial", 12, "bold"), bg=COLOR_FONDO, fg="#27ae60")
    lbl_total.pack(pady=10, anchor=tk.E, padx=20)


# =============================================================================
# ESTADO DE RESULTADOS MENSUAL (gerente-only)
# =============================================================================
def mostrar_rendimientos(frame):
    limpiar_frame(frame)
    crear_titulo(frame, "Margen Bruto Mensual")
    crear_subtitulo(frame, "Margen bruto calculado sobre la mercadería vendida durante el período")
    
    panel = tk.LabelFrame(frame, text=" Resumen mensual ", bg=COLOR_FONDO)
    panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    columnas = ("Mes", "Ventas", "Costos", "Margen Bruto")
    tree = ttk.Treeview(panel, columns=columnas, show="headings")
    
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Traemos los datos de todo el negocio
    datos = procesar_rendimientos_mensuales() 
    for d in datos:        
        tree.insert("", tk.END, values=(
            d['mes'], 
            formatear_moneda(d['total_ventas']), 
            formatear_moneda(d['total_costos']), 
            formatear_moneda(d['ganancia'])
        ))


# =============================================================================
# RANKING DE PRODUCTOS (TOP 10)
# =============================================================================
def mostrar_ranking_productos(frame):
    limpiar_frame(frame)
    crear_titulo(frame, "Ranking de Productos")
    crear_subtitulo(frame, "Top 10 de artículos más vendidos por volumen de unidades.")

    columnas = ("Puesto", "Producto", "Marca", "Unidades Vendidas", "Ingresos Generados")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=15)
    
    anchos = {"Puesto": 60, "Producto": 250, "Marca": 120, "Unidades Vendidas": 130, "Ingresos Generados": 150}
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=anchos.get(col, 100))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

    ranking = procesar_ranking_productos(10)
    
    for index, fila in enumerate(ranking, start=1):
        medalla = f"{index}"      

        tree.insert("", tk.END, values=(
            medalla,
            fila['descripcion'],
            fila['marca'],
            f"{fila['total_unidades']} u.",
            formatear_moneda(fila['ingresos_generados'])
        ))


# =============================================================================
# VENTAS POR FORMA DE PAGO
# =============================================================================
def mostrar_formas_pago(frame):
    """
    PROPÓSITO: ventas agrupadas por forma de pago.
    """
    limpiar_frame(frame)
    crear_titulo(frame, "Ventas por Forma de Pago")
    crear_subtitulo(frame, "Análisis de ingresos y cantidad de transacciones según el medio de pago.")

    # Contenedor para la tabla
    panel = tk.LabelFrame(frame, text=" Resultados Analíticos ", bg=COLOR_FONDO)
    panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Definir columnas de la grilla
    columnas = ("Forma de Pago", "Cantidad de Ventas", "Total Ingresos")
    tree = ttk.Treeview(panel, columns=columnas, show="headings", height=10)

    # Configurar cabeceras y centrado
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=150)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Obtener datos de la capa lógica (¡sin by-passing!)
    datos = procesar_ventas_por_forma_pago()

    # Llenar la tabla iterando los diccionarios
    for d in datos:
        tree.insert("", tk.END, values=(
            d['forma_pago'],
            d['cantidad_ventas'],
            formatear_moneda(d['total_ingresos'])
        ))