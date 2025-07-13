from flask import Blueprint, render_template, request, jsonify
from app.tamizado.forms import FormularioTamizado
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
from scipy import stats

bp_tamizado = Blueprint('tamizado', __name__)

@bp_tamizado.route('/', methods=['GET', 'POST'])
def analisis_granulometrico():
    formulario = FormularioTamizado()

    resultados_gates = None
    grafico_gates = None
    tabla_datos = None

    if request.method == 'POST':
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla de datos base
            df = crear_tabla_granulometrica(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Calcular modelo Gates-Gaudin-Schuhmann
            resultados_gates, grafico_gates = calcular_gates_gaudin_schuhmann(df)

    return render_template('tamizado/analisis.html',
                         formulario=formulario,
                         resultados_gates=resultados_gates,
                         grafico_gates=grafico_gates,
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
    Modelo Gates Gaudin Schuhmann: P(d) = (d/dₘₐₓ)ⁿ × 100
    Donde:
    - P(d) = % acumulado pasante para d
    - d = Tamaño de partícula (μm o mm)
    - dₘₐₓ = Tamaño máximo (μm o mm)
    - n = Exponente de distribución
    """
    try:
        # Filtrar datos válidos (porcentaje pasante > 0 y < 100)
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] < 100)].copy()

        if len(df_valid) < 3:
            return None, None

        # Datos para el ajuste
        d = df_valid['abertura'].values  # Tamaño de partícula
        P_d = df_valid['porcentaje_pasante'].values / 100  # % pasante como fracción

        # Transformación logarítmica: log(P(d)) = n*log(d) - n*log(dₘₐₓ)
        log_d = np.log(d)
        log_P_d = np.log(P_d)

        # Regresión lineal para encontrar n y dₘₐₓ
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_d, log_P_d)

        n = slope  # Exponente de distribución
        d_max = np.exp(-intercept / slope)  # Tamaño máximo
        r2 = r_value ** 2  # Coeficiente de determinación

        # Generar curva teórica usando la fórmula P(d) = (d/dₘₐₓ)ⁿ × 100
        d_teoria = np.logspace(np.log10(d.min()), np.log10(d.max()), 100)
        P_d_teoria = 100 * (d_teoria / d_max) ** n

        # Crear gráfico
        fig = go.Figure()

        # Datos experimentales
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers+lines',
            name='Datos Experimentales',
            marker=dict(size=8, color='blue'),
            line=dict(color='blue', width=2, dash='dot')
        ))

        # Curva teórica Gates-Gaudin-Schuhmann
        fig.add_trace(go.Scatter(
            x=d_teoria,
            y=P_d_teoria,
            mode='lines',
            name=f'Gates-Gaudin-Schuhmann (R² = {r2:.4f})',
            line=dict(color='red', width=3)
        ))

        fig.update_layout(
            title='Modelo Gates-Gaudin-Schuhmann: P(d) = (d/dₘₐₓ)ⁿ × 100',
            xaxis_title='Tamaño de partícula d (mm)',
            yaxis_title='Porcentaje acumulado pasante P(d) (%)',
            xaxis_type='log',
            yaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        resultados = {
            'd_max': d_max,
            'n': n,
            'r2': r2,
            'ecuacion': f'P(d) = (d/{d_max:.3f})^{n:.3f} × 100'
        }

        return resultados, grafico_json

    except Exception as e:
        print(f"Error en Gates-Gaudin-Schuhmann: {e}")
        return None, None