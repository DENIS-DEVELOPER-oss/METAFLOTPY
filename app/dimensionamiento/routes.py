
from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
import math

bp_dimensionamiento = Blueprint('dimensionamiento', __name__)

@bp_dimensionamiento.route('/')
def dimensionamiento():
    return render_template('dimensionamiento/dimensionamiento.html')

@bp_dimensionamiento.route('/molino-barras', methods=['GET', 'POST'])
def molino_barras():
    """Dimensionamiento de Molino de Barras"""
    resultados = None
    grafico = None
    
    if request.method == 'POST':
        try:
            # Datos de entrada
            F = float(request.form.get('capacidad_tratamiento', 0))
            Wi = float(request.form.get('indice_trabajo', 0))
            P80 = float(request.form.get('p80_producto', 0))
            F80 = float(request.form.get('f80_alimentacion', 0))
            pb = float(request.form.get('densidad_carga', 0))
            L_D = float(request.form.get('relacion_largo_diametro', 1.5))
            
            # Cálculos
            resultados = calcular_molino_barras(F, Wi, P80, F80, pb, L_D)
            grafico = crear_grafico_molino_barras(resultados)
            
        except Exception as e:
            print(f"Error en cálculo molino de barras: {e}")
    
    return render_template('dimensionamiento/molino_barras.html', 
                         resultados=resultados, grafico=grafico)

@bp_dimensionamiento.route('/molino-bolas', methods=['GET', 'POST'])
def molino_bolas():
    """Dimensionamiento de Molino de Bolas"""
    resultados = None
    grafico = None
    
    if request.method == 'POST':
        try:
            # Datos de entrada
            F = float(request.form.get('capacidad_tratamiento', 0))
            Wi = float(request.form.get('indice_trabajo', 0))
            P80 = float(request.form.get('p80_producto', 0))
            F80 = float(request.form.get('f80_alimentacion', 0))
            pb = float(request.form.get('densidad_carga', 0))
            L_D = float(request.form.get('relacion_largo_diametro', 1.0))
            
            # Cálculos
            resultados = calcular_molino_bolas(F, Wi, P80, F80, pb, L_D)
            grafico = crear_grafico_molino_bolas(resultados)
            
        except Exception as e:
            print(f"Error en cálculo molino de bolas: {e}")
    
    return render_template('dimensionamiento/molino_bolas.html', 
                         resultados=resultados, grafico=grafico)

@bp_dimensionamiento.route('/hidrociclones', methods=['GET', 'POST'])
def hidrociclones():
    """Equipos Clasificadores (Hidrociclones)"""
    resultados = None
    grafico = None
    
    if request.method == 'POST':
        try:
            # Datos de entrada
            Q = float(request.form.get('caudal', 0))
            d50c = float(request.form.get('tamano_corte', 0))
            ps = float(request.form.get('densidad_solido', 0))
            pl = float(request.form.get('densidad_liquido', 0))
            mu = float(request.form.get('viscosidad', 0))
            
            # Cálculos
            resultados = calcular_hidrociclones(Q, d50c, ps, pl, mu)
            grafico = crear_grafico_hidrociclones(resultados)
            
        except Exception as e:
            print(f"Error en cálculo hidrociclones: {e}")
    
    return render_template('dimensionamiento/hidrociclones.html', 
                         resultados=resultados, grafico=grafico)

@bp_dimensionamiento.route('/separadores', methods=['GET', 'POST'])
def separadores():
    """Equipos Separadores (Jigs, mesas, espirales)"""
    resultados = None
    grafico = None
    
    if request.method == 'POST':
        try:
            # Datos de entrada
            ps = float(request.form.get('densidad_mineral', 0))
            pf = float(request.form.get('densidad_ganga', 0))
            d = float(request.form.get('tamano_particula', 0))
            g = float(request.form.get('aceleracion_gravitacional', 9.81))
            
            # Cálculos
            resultados = calcular_separadores(ps, pf, d, g)
            grafico = crear_grafico_separadores(resultados)
            
        except Exception as e:
            print(f"Error en cálculo separadores: {e}")
    
    return render_template('dimensionamiento/separadores.html', 
                         resultados=resultados, grafico=grafico)

@bp_dimensionamiento.route('/almacenamiento', methods=['GET', 'POST'])
def almacenamiento():
    """Equipos de Almacenamiento (silos, tolvas)"""
    resultados = None
    grafico = None
    
    if request.method == 'POST':
        try:
            # Datos de entrada
            pm = float(request.form.get('densidad_material', 0))
            H = float(request.form.get('altura_silo', 0))
            D = float(request.form.get('diametro_silo', 0))
            
            # Cálculos
            resultados = calcular_almacenamiento(pm, H, D)
            grafico = crear_grafico_almacenamiento(resultados)
            
        except Exception as e:
            print(f"Error en cálculo almacenamiento: {e}")
    
    return render_template('dimensionamiento/almacenamiento.html', 
                         resultados=resultados, grafico=grafico)

# Funciones de cálculo
def calcular_molino_barras(F, Wi, P80, F80, pb, L_D):
    """Calcular dimensiones de molino de barras"""
    try:
        # 1. Potencia de Bond
        W = 10 * Wi * F * (1/math.sqrt(P80) - 1/math.sqrt(F80))
        
        # 2. Volumen útil del molino (carga: fracción de llenado típica = 0.4)
        carga = 0.4
        V = F / (pb * carga)
        
        # 3. Dimensiones del molino (asumiendo cilíndrico)
        # V = π/4 * D² * L y L = L_D * D
        # V = π/4 * D² * L_D * D = π/4 * L_D * D³
        D = (4 * V / (math.pi * L_D)) ** (1/3)
        L = L_D * D
        
        return {
            'potencia_bond': round(W, 2),
            'volumen_util': round(V, 2),
            'diametro': round(D, 2),
            'longitud': round(L, 2),
            'relacion_L_D': L_D,
            'carga_fraccion': carga,
            'capacidad': F,
            'work_index': Wi,
            'p80_producto': P80,
            'f80_alimentacion': F80,
            'densidad_carga': pb
        }
    except Exception as e:
        print(f"Error en cálculos molino barras: {e}")
        return None

def calcular_molino_bolas(F, Wi, P80, F80, pb, L_D):
    """Calcular dimensiones de molino de bolas"""
    try:
        # 1. Potencia
        W = 10 * Wi * F * (1/math.sqrt(P80) - 1/math.sqrt(F80))
        
        # 2. Volumen útil (carga ≈ 0.35)
        carga = 0.35
        V = F / (pb * carga)
        
        # 3. Cálculo de dimensiones igual que molino de barras
        D = (4 * V / (math.pi * L_D)) ** (1/3)
        L = L_D * D
        
        return {
            'potencia_bond': round(W, 2),
            'volumen_util': round(V, 2),
            'diametro': round(D, 2),
            'longitud': round(L, 2),
            'relacion_L_D': L_D,
            'carga_fraccion': carga,
            'capacidad': F,
            'work_index': Wi,
            'p80_producto': P80,
            'f80_alimentacion': F80,
            'densidad_carga': pb
        }
    except Exception as e:
        print(f"Error en cálculos molino bolas: {e}")
        return None

def calcular_hidrociclones(Q, d50c, ps, pl, mu):
    """Calcular dimensiones de hidrociclones"""
    try:
        # Ley de Stokes (simplificada para d50)
        # d50c ≈ √(18μ * Q / (Δρ * g * A))
        delta_rho = ps - pl
        g = 9.81
        
        # Área requerida (estimación)
        A = (18 * mu * Q) / (delta_rho * g * (d50c ** 2))
        
        # Relación flujo Q = A * v
        v = Q / A if A > 0 else 0
        
        # Diámetro equivalente del ciclón
        D_ciclon = math.sqrt(4 * A / math.pi) if A > 0 else 0
        
        return {
            'caudal': Q,
            'tamano_corte': d50c,
            'densidad_solido': ps,
            'densidad_liquido': pl,
            'viscosidad': mu,
            'delta_rho': round(delta_rho, 2),
            'area_requerida': round(A, 4),
            'velocidad': round(v, 2),
            'diametro_ciclon': round(D_ciclon, 2)
        }
    except Exception as e:
        print(f"Error en cálculos hidrociclones: {e}")
        return None

def calcular_separadores(ps, pf, d, g):
    """Calcular parámetros de separadores gravitacionales"""
    try:
        # Factor de concentración
        C = (ps - pf) / pf
        
        # Velocidad terminal (Stokes)
        mu = 0.001  # Viscosidad del agua (Pa·s)
        vt = (g * (d ** 2) * (ps - pf)) / (18 * mu)
        
        return {
            'densidad_mineral': ps,
            'densidad_ganga': pf,
            'tamano_particula': d,
            'aceleracion_gravitacional': g,
            'factor_concentracion': round(C, 4),
            'velocidad_terminal': round(vt, 6),
            'diferencia_densidad': round(ps - pf, 2)
        }
    except Exception as e:
        print(f"Error en cálculos separadores: {e}")
        return None

def calcular_almacenamiento(pm, H, D):
    """Calcular parámetros de almacenamiento"""
    try:
        # Volumen del silo
        V = (math.pi / 4) * (D ** 2) * H
        
        # Capacidad en toneladas
        capacidad = V * pm
        
        return {
            'densidad_material': pm,
            'altura_silo': H,
            'diametro_silo': D,
            'volumen_silo': round(V, 2),
            'capacidad_toneladas': round(capacidad, 2)
        }
    except Exception as e:
        print(f"Error en cálculos almacenamiento: {e}")
        return None

# Funciones para crear gráficos
def crear_grafico_molino_barras(resultados):
    """Crear gráfico para molino de barras"""
    if not resultados:
        return None
    
    try:
        fig = go.Figure()
        
        # Gráfico de barras con los parámetros principales
        parametros = ['Potencia (kW)', 'Volumen (m³)', 'Diámetro (m)', 'Longitud (m)']
        valores = [resultados['potencia_bond'], resultados['volumen_util'], 
                  resultados['diametro'], resultados['longitud']]
        
        fig.add_trace(go.Bar(
            x=parametros,
            y=valores,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
            text=[f'{v:.2f}' for v in valores],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Dimensiones del Molino de Barras',
            xaxis_title='Parámetros',
            yaxis_title='Valores',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creando gráfico molino barras: {e}")
        return None

def crear_grafico_molino_bolas(resultados):
    """Crear gráfico para molino de bolas"""
    if not resultados:
        return None
    
    try:
        fig = go.Figure()
        
        # Gráfico de barras con los parámetros principales
        parametros = ['Potencia (kW)', 'Volumen (m³)', 'Diámetro (m)', 'Longitud (m)']
        valores = [resultados['potencia_bond'], resultados['volumen_util'], 
                  resultados['diametro'], resultados['longitud']]
        
        fig.add_trace(go.Bar(
            x=parametros,
            y=valores,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
            text=[f'{v:.2f}' for v in valores],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Dimensiones del Molino de Bolas',
            xaxis_title='Parámetros',
            yaxis_title='Valores',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creando gráfico molino bolas: {e}")
        return None

def crear_grafico_hidrociclones(resultados):
    """Crear gráfico para hidrociclones"""
    if not resultados:
        return None
    
    try:
        fig = go.Figure()
        
        # Gráfico de dispersión mostrando relación entre parámetros
        fig.add_trace(go.Scatter(
            x=[resultados['tamano_corte']],
            y=[resultados['velocidad']],
            mode='markers+text',
            marker=dict(size=20, color='blue'),
            text=[f'D50c: {resultados["tamano_corte"]:.1f}μm<br>v: {resultados["velocidad"]:.2f}m/s'],
            textposition='top center'
        ))
        
        fig.update_layout(
            title='Parámetros del Hidrociclón',
            xaxis_title='Tamaño de corte d50c (μm)',
            yaxis_title='Velocidad (m/s)',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creando gráfico hidrociclones: {e}")
        return None

def crear_grafico_separadores(resultados):
    """Crear gráfico para separadores"""
    if not resultados:
        return None
    
    try:
        fig = go.Figure()
        
        # Gráfico mostrando factor de concentración vs velocidad terminal
        fig.add_trace(go.Scatter(
            x=[resultados['factor_concentracion']],
            y=[resultados['velocidad_terminal']],
            mode='markers+text',
            marker=dict(size=25, color='green'),
            text=[f'C: {resultados["factor_concentracion"]:.3f}<br>vt: {resultados["velocidad_terminal"]:.6f}m/s'],
            textposition='top center'
        ))
        
        fig.update_layout(
            title='Parámetros de Separación Gravitacional',
            xaxis_title='Factor de Concentración C',
            yaxis_title='Velocidad Terminal (m/s)',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creando gráfico separadores: {e}")
        return None

def crear_grafico_almacenamiento(resultados):
    """Crear gráfico para almacenamiento"""
    if not resultados:
        return None
    
    try:
        fig = go.Figure()
        
        # Gráfico de barras mostrando dimensiones del silo
        parametros = ['Altura (m)', 'Diámetro (m)', 'Volumen (m³)', 'Capacidad (t)']
        valores = [resultados['altura_silo'], resultados['diametro_silo'], 
                  resultados['volumen_silo'], resultados['capacidad_toneladas']]
        
        fig.add_trace(go.Bar(
            x=parametros,
            y=valores,
            marker_color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'],
            text=[f'{v:.2f}' for v in valores],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Dimensiones del Silo de Almacenamiento',
            xaxis_title='Parámetros',
            yaxis_title='Valores',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creando gráfico almacenamiento: {e}")
        return None
