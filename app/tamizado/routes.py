from flask import Blueprint, render_template, request, jsonify
from app.tamizado.forms import FormularioTamizado
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
from scipy.optimize import curve_fit
from scipy import stats

bp_tamizado = Blueprint('tamizado', __name__)

@bp_tamizado.route('/', methods=['GET', 'POST'])
def analisis_granulometrico():
    formulario = FormularioTamizado()

    resultados = {}
    graficos = {}
    tabla_datos = None

    if request.method == 'POST':
        modelo = request.form.get('modelo')
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla de datos base
            df = crear_tabla_granulometrica(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            if modelo == 'gates':
                resultados['gates'], graficos['gates'] = calcular_gates_gaudin_schuhmann(df)
            elif modelo == 'rosin':
                resultados['rosin'], graficos['rosin'] = calcular_rosin_rammler(df)
            elif modelo == 'regresion':
                resultados['regresion'], graficos['regresion'] = calcular_regresion_lineal(df)

    return render_template('tamizado/analisis.html',
                         formulario=formulario,
                         resultados_gates=resultados.get('gates'),
                         resultados_rosin=resultados.get('rosin'),
                         resultados_regresion=resultados.get('regresion'),
                         grafico_gates=graficos.get('gates'),
                         grafico_rosin=graficos.get('rosin'),
                         grafico_regresion=graficos.get('regresion'),
                         tabla_datos=tabla_datos)

def crear_tabla_granulometrica(aberturas, pesos_retenidos, peso_total):
    """Crear tabla base con cálculos granulométricos"""
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })

    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)

    # Calcular porcentajes
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()
    df['porcentaje_pasante'] = 100 - df['porcentaje_acumulado']

    return df

def calcular_gates_gaudin_schuhmann(df):
    """
    Modelo Gates Gaudin Schuhmann: P = (x/k)^m
    Donde P = % pasante, x = abertura, k = tamaño máximo, m = módulo de distribución
    """
    try:
        # Filtrar datos válidos (porcentaje pasante > 0)
        df_valid = df[df['porcentaje_pasante'] > 0].copy()

        x = df_valid['abertura'].values
        y = df_valid['porcentaje_pasante'].values / 100  # Convertir a fracción

        # Transformación logarítmica: log(P) = m*log(x) - m*log(k)
        log_x = np.log(x)
        log_y = np.log(y)

        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)

        m = slope
        k = np.exp(-intercept / slope)
        r2 = r_value ** 2

        # Generar curva teórica
        x_teoria = np.logspace(np.log10(x.min()), np.log10(x.max()), 100)
        y_teoria = 100 * (x_teoria / k) ** m

        # Crear gráfico
        fig = go.Figure()

        # Datos experimentales
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers',
            name='Datos Experimentales',
            marker=dict(size=8, color='blue')
        ))

        # Curva teórica
        fig.add_trace(go.Scatter(
            x=x_teoria,
            y=y_teoria,
            mode='lines',
            name=f'Gates Gaudin Schuhmann (R² = {r2:.4f})',
            line=dict(color='red', width=2)
        ))

        fig.update_layout(
            title='Modelo Gates Gaudin Schuhmann',
            xaxis_title='Abertura (mm)',
            yaxis_title='Porcentaje Pasante (%)',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest'
        )

        grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        resultados = {
            'k': k,
            'm': m,
            'r2': r2,
            'ecuacion': f'P = (x/{k:.3f})^{m:.3f}'
        }

        return resultados, grafico_json

    except Exception as e:
        print(f"Error en Gates Gaudin Schuhmann: {e}")
        return None, None

def calcular_rosin_rammler(df):
    """
    Modelo Rosin Rammler: P = 1 - exp(-(x/x0)^n)
    Donde P = % pasante, x = abertura, x0 = tamaño característico, n = módulo de uniformidad
    """
    try:
        # Filtrar datos válidos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] < 100)].copy()

        x = df_valid['abertura'].values
        y = df_valid['porcentaje_pasante'].values / 100  # Convertir a fracción

        # Transformación: ln(ln(1/(1-P))) = n*ln(x) - n*ln(x0)
        # Pero para evitar problemas con log(0), usamos P_retenido = 1 - P_pasante
        p_retenido = 1 - y
        p_retenido = np.where(p_retenido <= 0, 1e-6, p_retenido)  # Evitar log(0)
        p_retenido = np.where(p_retenido >= 1, 1-1e-6, p_retenido)  # Evitar log(0)

        ln_ln_term = np.log(-np.log(1 - p_retenido))
        ln_x = np.log(x)

        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(ln_x, ln_ln_term)

        n = slope
        x0 = np.exp(-intercept / slope)
        r2 = r_value ** 2

        # Generar curva teórica
        x_teoria = np.logspace(np.log10(x.min()), np.log10(x.max()), 100)
        y_teoria = 100 * (1 - np.exp(-(x_teoria / x0) ** n))

        # Crear gráfico
        fig = go.Figure()

        # Datos experimentales
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers',
            name='Datos Experimentales',
            marker=dict(size=8, color='green')
        ))

        # Curva teórica
        fig.add_trace(go.Scatter(
            x=x_teoria,
            y=y_teoria,
            mode='lines',
            name=f'Rosin Rammler (R² = {r2:.4f})',
            line=dict(color='orange', width=2)
        ))

        fig.update_layout(
            title='Modelo Rosin Rammler',
            xaxis_title='Abertura (mm)',
            yaxis_title='Porcentaje Pasante (%)',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest'
        )

        grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        resultados = {
            'x0': x0,
            'n': n,
            'r2': r2,
            'ecuacion': f'P = 1 - exp(-(x/{x0:.3f})^{n:.3f})'
        }

        return resultados, grafico_json

    except Exception as e:
        print(f"Error en Rosin Rammler: {e}")
        return None, None

def calcular_regresion_lineal(df):
    """
    Regresión lineal simple entre log(abertura) y % pasante
    """
    try:
        # Filtrar datos válidos
        df_valid = df[df['porcentaje_pasante'] > 0].copy()

        x = np.log10(df_valid['abertura'].values)
        y = df_valid['porcentaje_pasante'].values

        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r2 = r_value ** 2

        # Generar línea teórica
        x_teoria_log = np.linspace(x.min(), x.max(), 100)
        y_teoria = slope * x_teoria_log + intercept
        x_teoria = 10 ** x_teoria_log

        # Crear gráfico
        fig = go.Figure()

        # Datos experimentales
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers',
            name='Datos Experimentales',
            marker=dict(size=8, color='purple')
        ))

        # Línea de regresión
        fig.add_trace(go.Scatter(
            x=x_teoria,
            y=y_teoria,
            mode='lines',
            name=f'Regresión Lineal (R² = {r2:.4f})',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.update_layout(
            title='Regresión Lineal - log(Abertura) vs % Pasante',
            xaxis_title='Abertura (mm)',
            yaxis_title='Porcentaje Pasante (%)',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest'
        )

        grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        resultados = {
            'pendiente': slope,
            'intercepto': intercept,
            'r2': r2,
            'ecuacion': f'y = {slope:.4f}x + {intercept:.4f}'
        }

        return resultados, grafico_json

    except Exception as e:
        print(f"Error en Regresión Lineal: {e}")
        return None, None