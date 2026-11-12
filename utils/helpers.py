"""
===============================================================================
PROYECTO: Tecno Store - Sistema de Gestión y Punto de Venta
MÓDULO: helpers.py
CAPA: Utilidades / Soporte (Utils)
DESCRIPCIÓN:
Funciones auxiliares y genéricas del sistema (formateo de fechas, strings, 
monedas y validaciones básicas de datos de entrada).
===============================================================================
"""

def calcular_iva(subtotal):
    """
    PROPÓSITO: Calcula el monto correspondiente al Impuesto al Valor Agregado (21%) 
               sobre un monto base.


    PARÁMETROS:  
        :subtotal: (float) Monto base sobre el cual calcular el impuesto.

    RETORNO: 
        :monto_iva: (float) El valor calculado del impuesto.
    """
    iva = 0.21
    monto_iva = float(subtotal) * iva
    return monto_iva


def formatear_moneda(monto):
    """
    PROPÓSITO: Convierte un valor numérico a un formato de texto amigable para la vista,
               simulando el formato moneda local (ej: $ 25.000,00).


    PARÁMETROS:  
        :monto: (float/int) El valor numérico crudo.

    RETORNO: 
        :monto_formateado: (str) String con símbolo de pesos, separador de miles y 2 decimales.
    """
    # Formateamos con comas para miles y puntos para decimales nativo de Python
    # y luego los invertimos para el formato tradicional latinoamericano.
    monto_str = f"{float(monto):,.2f}"
    monto_latam = monto_str.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"$ {monto_latam}"