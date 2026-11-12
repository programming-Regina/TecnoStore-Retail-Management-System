"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: consultas_view.py
CAPA: Vista (views)
DESCRIPCIÓN:
Pantallas de consulta utilizadas por distintos roles.

Estas vistas serán utilizadas principalmente por:
- Gerente
- Vendedor
- Depositero
===============================================================================
"""
import tkinter as tk
from tkinter import ttk

# Importa los componentes 
from views.components import (
    crear_titulo, 
    crear_boton_accion, 
    limpiar_frame,
    crear_etiqueta_info,
    crear_etiqueta_error,
    crear_combobox,
    crear_contenedor_resultados,
    mostrar_mensaje_en_resultados
)

# Variable global para mantener el estado del usuario logueado
ROL_USUARIO_LOGUEADO = None # Valor por defecto seguro

def asignar_rol_logueado(rol_recibido):
    """
    Función para que el Login actualice el rol global.
    """
    global ROL_USUARIO_LOGUEADO
    ROL_USUARIO_LOGUEADO = rol_recibido

# DICCIONARIO INTERNO (Para TP BBDD - No altera la botonera principal de MENU_ROLES)
DICCIONARIO_CONSULTAS = {
    "administrador": [
        # --- Básicas ---
        "1. Productos activos ordenados por precio de venta (Básica)",
        "2. Listar usuarios por rol (Básica)",
        "3. Productos con stock por debajo del mínimo (Básica)",
        "4. Proveedores activos (Básica)",
        "5. Buscar producto por descripción (LIKE) (Básica)",
        # --- JOIN ---
        "6. Ventas con nombre del vendedor que las registró (JOIN)",
        "7. Detalle de venta con descripción y precio de cada producto (JOIN)",
        "8. Compras con nombre del proveedor (JOIN)",
        "9. Productos que nunca fueron comprados a ningún proveedor (LEFT JOIN + NULL) (JOIN)",
        # --- GROUP BY + HAVING ---
        "10. Total vendido por mes (GROUP BY)",
        "11. Costos del mes (mercadería comprada) (GROUP BY)",
        "12. Ganancia estimada (ventas - costos) (GROUP BY)",
        "13. Producto más vendido por mes (GROUP BY)",
        "14. Categoría más vendida (GROUP BY)",
        "15. Cantidad de ventas por mes (GROUP BY)",
        "16. Ticket promedio general (GROUP BY)",
        "17. Categorías con más de 5 productos activos (HAVING) (GROUP BY + HAVING)",
        "18. Vendedores con ticket promedio superior a un monto (HAVING) (GROUP BY + HAVING)",
        "19. Proveedores frecuentes (más de 5 compras) (HAVING) (GROUP BY + HAVING)",
        # --- Subconsultas ---
        "20. Producto con el mayor stock actual (Subconsulta escalar)",
        "21. Productos vendidos pagados con crédito (Subconsulta IN)",
        "22. Vendedores con al menos una venta registrada (Subconsulta EXISTS)",
        "23. Productos cuyo precio supera el promedio de su categoría (Subconsulta correlacionada)"
    ],
    "gerente": [
        # --- JOIN ---
        "1. Ventas con nombre del vendedor que las registró (JOIN)",
        # --- GROUP BY + HAVING ---
        "2. Total vendido por mes (GROUP BY)",
        "3. Costos del mes (mercadería comprada) (GROUP BY)",
        "4. Ganancia estimada (ventas - costos) (GROUP BY)",
        "5. Producto más vendido por mes (GROUP BY)",
        "6. Categoría más vendida (GROUP BY)",
        "7. Cantidad de ventas por mes (GROUP BY)",
        "8. Ticket promedio general (GROUP BY)",
        "9. Vendedores con ticket promedio superior a un monto (HAVING) (GROUP BY + HAVING)",
        # --- Subconsultas ---
        "10. Productos vendidos pagados con crédito (Subconsulta IN)",
        "11. Vendedores con al menos una venta registrada (Subconsulta EXISTS)",
        "12. Productos cuyo precio supera el promedio de su categoría (Subconsulta correlacionada)"
    ],
    "vendedor": [
        # --- Básicas ---
        "1. Productos activos ordenados por precio de venta (Básica)",
        "2. Buscar producto por descripción (LIKE) (Básica)",
        # --- JOIN ---
        "3. Detalle de venta con descripción y precio de cada producto (JOIN)",
        # --- Subconsultas ---
        "4. Productos cuyo precio supera el promedio de su categoría (Subconsulta correlacionada)"
    ],
    "depositero": [
        # --- Básicas ---
        "1. Productos activos ordenados por precio de venta (Básica)",
        "2. Productos con stock por debajo del mínimo (Básica)",
        "3. Listar todos los proveedores activos (Básica)",
        "4. Buscar producto por descripción (LIKE) (Básica)",
        # --- JOIN ---
        "5. Compras con nombre del proveedor (JOIN)",
        "6. Productos que nunca fueron comprados a ningún proveedor (LEFT JOIN + NULL) (JOIN)",
        # --- GROUP BY + HAVING ---
        "7. Categorías con más de 5 productos activos (HAVING) (GROUP BY + HAVING)",
        "8. Proveedores frecuentes (más de 5 compras) (HAVING) (GROUP BY + HAVING)",
        # --- Subconsultas ---
        "9. Producto con el mayor stock actual (Subconsulta escalar)"
    ]
}


# =============================================================================
# DECIDE QUIÉN ENTRA A QUÉ FUNCIONES
# =============================================================================
def obtener_consultas_por_rol(rol):
    """
    Usa la variable ROL_USUARIO_LOGUEADO para extraer las consultas
    requeridas del diccionario técnico, garantizando las 20 opciones para el TPI.
    """
    # Forzamos minúsculas por si el rol global 
    rol_key = str(rol).lower() if rol else "vendedor"
    
    # Retorna la lista de strings para el Combobox de Tkinter
    return DICCIONARIO_CONSULTAS.get(rol_key, ["No hay consultas asignadas para este rol"])
    


# =============================================================================
# PANTALLA DE DEMOSTRACIÓN DE CONSULTAS AVANZADAS
# =============================================================================
def mostrar_consultas_avanzadas(frame):
    """
    Dibuja la pantalla de consultas en el frame central de la aplicación.
    """
    limpiar_frame(frame)
    
    rol_actual = ROL_USUARIO_LOGUEADO
    crear_titulo(frame, f"Consultas Avanzadas - Panel de {rol_actual.capitalize()}")
    
    consultas_permitidas = obtener_consultas_por_rol(rol_actual)
    
    # 1. Manejo de error si no hay consultas
    if len(consultas_permitidas) == 0:
        crear_etiqueta_error(frame, "No tiene consultas asignadas para SU rol.")
        return

    # 2. Instrucciones y Selector
    crear_etiqueta_info(frame, "Seleccione la consulta técnica a ejecutar:")
    combo_consultas = crear_combobox(frame, valores=consultas_permitidas)
    
    # 3. Contenedor de resultados
    frame_resultados = crear_contenedor_resultados(frame)
    mostrar_mensaje_en_resultados(frame_resultados, "Los resultados aparecerán aquí.")
    
    # 4. Lógica de ejecución
    def ejecutar_consulta_seleccionada():
        seleccion = combo_consultas.get()
        
        # Evaluamos paso a paso cuál eligió el usuario
        if "1. Productos sobre promedio" in seleccion:
            mostrar_mensaje_en_resultados(frame_resultados, "[BD] Ejecutando: Productos sobre el promedio...")
            
        elif "2. Listado de vendedores activos" in seleccion:
            mostrar_mensaje_en_resultados(frame_resultados, "[BD] Ejecutando: Vendedores activos con JOIN...")
            
        elif "3. Producto con mayor stock" in seleccion:
            mostrar_mensaje_en_resultados(frame_resultados, "[BD] Ejecutando: Mayor stock con Subconsulta...")
            
        elif "4. Productos sin ventas" in seleccion:
            mostrar_mensaje_en_resultados(frame_resultados, "[BD] Ejecutando: Productos sin ventas con IN...")
            
        elif "5. Rendimiento por vendedor" in seleccion:
            mostrar_mensaje_en_resultados(frame_resultados, "[BD] Ejecutando: Rendimiento agrupado (GROUP BY)...")

    # 5. Botón de acción
    crear_boton_accion(frame, "Ejecutar Consulta", ejecutar_consulta_seleccionada)

