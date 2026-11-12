"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: reportes.py
CAPA: Lógica de Negocio (Controlador / Servicios)
DESCRIPCIÓN:
Procesa los datos analíticos del sistema. Consume vistas SQL (como rendimientos 
mensuales y rankings) para estructurar la información requerida por la interfaz.
===============================================================================
"""

from db.dao import obtener_rendimiento_vendedores, obtener_ranking_productos,obtener_ventas_agrupadas_por_usuario, obtener_rendimientos_mensuales, obtener_ventas_por_forma_pago


def procesar_rendimiento_vendedores():
    """
    petición del rendimiento mensual de los vendedores.    
    """
    # pedimos datos al dao
    datos_crudos = obtener_rendimiento_vendedores()
    
    # si no hay datos, va lista vacía
    if not datos_crudos:
        return []
        
    return datos_crudos


def procesar_ranking_productos(limite=10):
    """
    ranking de productos más vendidos.
    controla que el limite sea valido
    """
    if limite <= 0:
        limite = 10 # Forzamos un límite
        
    ranking = obtener_ranking_productos(limite)
    
    return ranking if ranking else []


def procesar_mis_ventas(nombre_vendedor):
    """
    trae ventas del dao por mes y del vendedor logueado
    """
    historial = obtener_ventas_agrupadas_por_usuario(nombre_vendedor)
    return historial if historial else []



def procesar_rendimientos_mensuales():
    """
    trae del dao 
    """
    datos = obtener_rendimientos_mensuales()
    # Mapeamos los nombres de las columnas que vienen de SQL 
    # a los nombres que espera la vista
    datos_mapeados = []
    for d in datos:
        datos_mapeados.append({
            'mes': d['mes'],
            'total_ventas': d['total_vendido'],    
            'total_costos': d['total_costos'],
            'ganancia': d['ganancia_estimada']    
        })
    return datos_mapeados



def procesar_ventas_por_forma_pago():
    """
    PROPÓSITO: Puente lógico para el reporte de ventas por forma de pago.
    """
    datos = obtener_ventas_por_forma_pago()
    return datos if datos else []