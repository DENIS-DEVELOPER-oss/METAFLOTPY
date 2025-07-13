
from flask import Blueprint, render_template, request, jsonify
from app.valorizacion.forms import FormularioValorizacion
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json

bp_valorizacion = Blueprint('valorizacion', __name__)

@bp_valorizacion.route('/', methods=['GET', 'POST'])
def valorizacion():
    """Valorización de concentrados"""
    formulario = FormularioValorizacion()
    
    resultados_calculo = None
    grafico_barras = None
    tabla_resumen = None

    if request.method == 'POST':
        # Obtener datos del formulario
        q = float(request.form.get('cantidad_concentrado', 0))  # Cantidad de concentrado (t/mes)
        l = float(request.form.get('ley_metal', 0))  # Ley del metal en el concentrado (%)
        r = float(request.form.get('recuperacion', 0))  # Recuperación metalúrgica (%)
        p = float(request.form.get('precio_metal', 0))  # Precio del metal (USD/ton o USD/oz)
        c_tr = float(request.form.get('costo_tratamiento', 0))  # Costo de tratamiento (USD/t de concentrado)
        p_pen = float(request.form.get('penalidades', 0))  # Penalidades por impurezas (USD/t)
        f = float(request.form.get('factor_conversion', 31.1035))  # Factor de conversión según el metal

        if q > 0 and l > 0 and p > 0:
            # Realizar cálculos de valorización
            resultados_calculo = calcular_valorizacion(q, l, r, p, c_tr, p_pen, f)
            
            # Crear gráfico de barras
            grafico_barras = crear_grafico_valorizacion(resultados_calculo)
            
            # Crear tabla resumen
            tabla_resumen = crear_tabla_resumen(resultados_calculo)

    return render_template('valorizacion/valorizacion.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_barras=grafico_barras,
                         tabla_resumen=tabla_resumen)

def calcular_valorizacion(q, l, r, p, c_tr, p_pen, f):
    """Calcular valorización completa del concentrado"""
    try:
        # 1. Valor bruto del concentrado
        # Valor Bruto = Q × (L/100) × F × P
        valor_bruto = q * (l / 100) * f * p
        
        # 2. Deducciones totales
        # Deducciones = Q × (C_tr + P_pen)
        deducciones_totales = q * (c_tr + p_pen)
        
        # 3. Valor neto del concentrado
        # Valor Neto = Valor Bruto - Deducciones
        valor_neto = valor_bruto - deducciones_totales
        
        # 4. Valor neto por tonelada
        # USD/t = Valor Neto / Q
        valor_neto_por_tonelada = valor_neto / q if q > 0 else 0
        
        # Componentes detallados
        metal_pagable = q * (l / 100)  # Toneladas de metal pagable
        ingresos_por_metal = metal_pagable * f * p  # Ingresos totales por el metal
        costos_tratamiento = q * c_tr  # Costos de tratamiento
        costos_penalidades = q * p_pen  # Costos por penalidades
        
        # Interpretación
        interpretacion = {
            'valor_bruto_desc': f'El valor bruto representa el ingreso potencial sin costos: ${valor_bruto:,.2f} USD',
            'deducciones_desc': f'Las deducciones reflejan descuentos por tratamiento y penalidades: ${deducciones_totales:,.2f} USD',
            'valor_neto_desc': f'El valor neto es el ingreso real por concentrado vendido: ${valor_neto:,.2f} USD',
            'escenarios': f'Se puede usar para simular escenarios: cambios de ley ({l}%), precio (${p}) o costos.'
        }
        
        # Ejemplo de cálculo paso a paso
        ejemplo_calculo = {
            'paso1': f'Valor Bruto = {q} × ({l}/100) × {f} × {p} = {q} × {l/100:.4f} × {f} × {p} = ${valor_bruto:,.2f} USD',
            'paso2': f'Deducciones = {q} × ({c_tr} + {p_pen}) = {q} × {c_tr + p_pen} = ${deducciones_totales:,.2f} USD',
            'paso3': f'Valor Neto = {valor_bruto:,.2f} - {deducciones_totales:,.2f} = ${valor_neto:,.2f} USD'
        }
        
        resultados = {
            # Datos de entrada
            'q': q,
            'l': l,
            'r': r,
            'p': p,
            'c_tr': c_tr,
            'p_pen': p_pen,
            'f': f,
            
            # Resultados principales
            'valor_bruto': valor_bruto,
            'deducciones_totales': deducciones_totales,
            'valor_neto': valor_neto,
            'valor_neto_por_tonelada': valor_neto_por_tonelada,
            
            # Componentes detallados
            'metal_pagable': metal_pagable,
            'ingresos_por_metal': ingresos_por_metal,
            'costos_tratamiento': costos_tratamiento,
            'costos_penalidades': costos_penalidades,
            
            # Análisis adicional
            'interpretacion': interpretacion,
            'ejemplo_calculo': ejemplo_calculo,
            
            # Fórmulas utilizadas
            'formulas': {
                'valor_bruto': 'Valor Bruto = Q × (L/100) × F × P',
                'deducciones': 'Deducciones = Q × (C_tr + P_pen)',
                'valor_neto': 'Valor Neto = Valor Bruto - Deducciones',
                'valor_por_tonelada': 'USD/t = Valor Neto / Q'
            }
        }
        
        return resultados
        
    except Exception as e:
        print(f"Error en cálculo de valorización: {e}")
        return None

def crear_grafico_valorizacion(resultados):
    """Crear gráfico de barras para valorización"""
    try:
        fig = go.Figure()
        
        # Datos para el gráfico
        categorias = ['Valor Bruto', 'Costo Tratamiento', 'Penalidades', 'Valor Neto']
        valores = [
            resultados['valor_bruto'],
            -resultados['costos_tratamiento'],  # Negativo para mostrar como reducción
            -resultados['costos_penalidades'],   # Negativo para mostrar como reducción
            resultados['valor_neto']
        ]
        colores = ['green', 'orange', 'red', 'blue']
        
        # Crear barras
        fig.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=colores,
            text=[f'${v:,.0f}' for v in valores],
            textposition='auto',
            name='Valorización'
        ))
        
        fig.update_layout(
            title='Análisis de Valorización del Concentrado',
            xaxis_title='Componentes',
            yaxis_title='Valor (USD)',
            yaxis_tickformat='$,.0f',
            showlegend=False,
            template='plotly_white',
            height=500
        )
        
        # Línea de referencia en cero
        fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Punto de equilibrio")
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        print(f"Error creando gráfico de valorización: {e}")
        return None

def crear_tabla_resumen(resultados):
    """Crear tabla resumen con ley, recuperación, precio e ingresos netos"""
    try:
        tabla = {
            'ley_concentrado': f"{resultados['l']:.2f}%",
            'recuperacion_metalurgica': f"{resultados['r']:.2f}%",
            'precio_metal': f"${resultados['p']:.2f} USD/{'oz' if resultados['f'] == 31.1035 else 'ton'}",
            'ingresos_netos': f"${resultados['valor_neto']:,.2f} USD",
            'valor_por_tonelada': f"${resultados['valor_neto_por_tonelada']:,.2f} USD/t",
            'metal_pagable': f"{resultados['metal_pagable']:.3f} t"
        }
        
        return tabla
        
    except Exception as e:
        print(f"Error creando tabla resumen: {e}")
        return None
