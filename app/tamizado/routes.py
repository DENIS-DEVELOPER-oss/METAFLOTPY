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

    resultados_calculo = None
    grafico_principal = None
    grafico_log_log = None
    tabla_datos = None

    if request.method == 'POST':
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla de datos según las fórmulas especificadas
            df = crear_tabla_granulometrica_especifica(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Crear gráficos según especificaciones
            grafico_principal = crear_grafico_granulometrico(df)
            grafico_log_log = crear_grafico_log_log_especifico(df)
            
            # Calcular regresión lineal para obtener n
            resultados_calculo = calcular_regresion_especifica(df)

    return render_template('tamizado/analisis.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_principal=grafico_principal,
                         grafico_log_log=grafico_log_log,
                         tabla_datos=tabla_datos)

def crear_tabla_granulometrica_especifica(aberturas, pesos_retenidos, peso_total):
    """
    Crear tabla con cálculos según las fórmulas especificadas:
    1. % Retenido por malla: %Ri = (Ri/T) × 100
    2. % Acumulado retenido: %AcumRi = Σ(%Rj) desde j=1 hasta i
    3. % Acumulado pasante: %Pi = 100 - %AcumRi
    """
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })

    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)

    # 1. % Retenido por malla: %Ri = (Ri/T) × 100
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100

    # 2. % Acumulado retenido: %AcumRi = Σ(%Rj) desde j=1 hasta i
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()

    # 3. % Acumulado pasante: %Pi = 100 - %AcumRi
    df['porcentaje_pasante'] = 100 - df['porcentaje_acumulado']

    return df

def crear_grafico_granulometrico(df):
    """Crear gráfico principal de distribución granulométrica"""
    try:
        fig = go.Figure()

        # Curva de % pasante
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers+lines',
            name='% Acumulado Pasante',
            marker=dict(size=8, color='blue'),
            line=dict(color='blue', width=3)
        ))

        # Curva de % retenido acumulado
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_acumulado'],
            mode='markers+lines',
            name='% Acumulado Retenido',
            marker=dict(size=8, color='red'),
            line=dict(color='red', width=3)
        ))

        fig.update_layout(
            title='Curvas Granulométricas',
            xaxis_title='Tamaño de partícula (mm)',
            yaxis_title='Porcentaje (%)',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico granulométrico: {e}")
        return None

def crear_grafico_log_log_especifico(df):
    """
    Crear gráfico log-log para obtener n según especificación:
    4. Logaritmos (para graficar y obtener n): log(di), log(%Pi)
    5. Regresión lineal en gráfico log-log para obtener n:
       Usa mínimos cuadrados para obtener la pendiente n de:
       log(%Pi) = n × log(di)
    """
    try:
        # Filtrar datos válidos para logaritmos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] < 100)].copy()
        
        if len(df_valid) < 2:
            return None

        fig = go.Figure()

        # Datos experimentales en log-log
        fig.add_trace(go.Scatter(
            x=df_valid['abertura'],
            y=df_valid['porcentaje_pasante'],
            mode='markers+lines',
            name='Datos Experimentales',
            marker=dict(size=10, color='blue'),
            line=dict(color='blue', width=2, dash='dot')
        ))

        fig.update_layout(
            title='Gráfico Log-Log para obtener n<br>log(%Pi) = n × log(di)',
            xaxis_title='Tamaño de partícula di (mm)',
            yaxis_title='% Acumulado Pasante %Pi (%)',
            xaxis_type='log',
            yaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico log-log: {e}")
        return None

def calcular_regresion_especifica(df):
    """
    Calcular regresión lineal según especificación:
    log(%Pi) = n × log(di)
    Usar mínimos cuadrados para obtener la pendiente n
    """
    try:
        # Filtrar datos válidos para logaritmos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] < 100)].copy()
        
        if len(df_valid) < 2:
            return None

        # 4. Logaritmos para graficar y obtener n
        log_di = np.log10(df_valid['abertura'].values)
        log_Pi = np.log10(df_valid['porcentaje_pasante'].values)

        # 5. Regresión lineal: log(%Pi) = n × log(di)
        # Usando mínimos cuadrados
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_di, log_Pi)

        n = slope  # La pendiente es el exponente n
        r2 = r_value ** 2

        # Datos para la tabla de logaritmos
        tabla_logaritmos = []
        for i, row in df_valid.iterrows():
            tabla_logaritmos.append({
                'abertura': row['abertura'],
                'porcentaje_pasante': row['porcentaje_pasante'],
                'log_di': np.log10(row['abertura']),
                'log_Pi': np.log10(row['porcentaje_pasante'])
            })

        resultados = {
            'n': n,
            'r2': r2,
            'ecuacion': f'log(%Pi) = {n:.3f} × log(di) + {intercept:.3f}',
            'tabla_logaritmos': tabla_logaritmos
        }

        return resultados

    except Exception as e:
        print(f"Error en cálculo de regresión: {e}")
        return None

@bp_tamizado.route('/rosin-rammler', methods=['GET', 'POST'])
def rosin_rammler():
    formulario = FormularioTamizado()

    resultados_calculo = None
    grafico_principal = None
    grafico_semilog = None
    tabla_datos = None

    if request.method == 'POST':
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]
        peso_total = float(request.form.get('peso_total', 0))

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla de datos para Rosin-Rammler
            df = crear_tabla_rosin_rammler(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Crear gráficos
            grafico_principal = crear_grafico_rosin_rammler(df)
            grafico_semilog = crear_grafico_semilog_rosin_rammler(df)
            
            # Calcular parámetros de Rosin-Rammler
            resultados_calculo = calcular_parametros_rosin_rammler(df)

    return render_template('tamizado/rosin_rammler.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_principal=grafico_principal,
                         grafico_semilog=grafico_semilog,
                         tabla_datos=tabla_datos)

def crear_tabla_rosin_rammler(aberturas, pesos_retenidos, peso_total):
    """
    Crear tabla con cálculos para Rosin-Rammler:
    R(d) = 100 * e^(-(d/d0)^n)
    """
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })

    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)

    # % Retenido por malla
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100

    # % Acumulado retenido
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()

    # R(d): % retenido acumulado (dato a calcular)
    df['R_d'] = df['porcentaje_acumulado']

    return df

def crear_grafico_rosin_rammler(df):
    """Crear gráfico principal de distribución Rosin-Rammler"""
    try:
        fig = go.Figure()

        # Curva experimental R(d)
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['R_d'],
            mode='markers+lines',
            name='R(d) Experimental',
            marker=dict(size=8, color='blue'),
            line=dict(color='blue', width=3)
        ))

        fig.update_layout(
            title='Distribución Rosin-Rammler<br>R(d) = 100 × e^(-(d/d₀)ⁿ)',
            xaxis_title='Tamaño de partícula d (mm)',
            yaxis_title='% Retenido Acumulado R(d) (%)',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico Rosin-Rammler: {e}")
        return None

def crear_grafico_semilog_rosin_rammler(df):
    """
    Crear gráfico semilogarítmico para obtener parámetros:
    ln[-ln(R(d)/100)] = n × ln(d) - n × ln(d₀)
    """
    try:
        # Filtrar datos válidos para logaritmos
        df_valid = df[(df['R_d'] > 0) & (df['R_d'] < 100)].copy()
        
        if len(df_valid) < 2:
            return None

        fig = go.Figure()

        # Datos experimentales
        ln_d = np.log(df_valid['abertura'].values)
        ln_ln_R = np.log(-np.log(df_valid['R_d'].values / 100))

        fig.add_trace(go.Scatter(
            x=ln_d,
            y=ln_ln_R,
            mode='markers+lines',
            name='Datos Experimentales',
            marker=dict(size=10, color='red'),
            line=dict(color='red', width=2, dash='dot')
        ))

        fig.update_layout(
            title='Gráfico Semilogarítmico Rosin-Rammler<br>ln[-ln(R(d)/100)] = n × ln(d) - n × ln(d₀)',
            xaxis_title='ln(d)',
            yaxis_title='ln[-ln(R(d)/100)]',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico semilog: {e}")
        return None

def calcular_parametros_rosin_rammler(df):
    """
    Calcular parámetros n y d₀ para Rosin-Rammler:
    ln[-ln(R(d)/100)] = n × ln(d) - n × ln(d₀)
    """
    try:
        # Filtrar datos válidos para logaritmos
        df_valid = df[(df['R_d'] > 0) & (df['R_d'] < 100)].copy()
        
        if len(df_valid) < 2:
            return None

        # Calcular ln(d) y ln[-ln(R(d)/100)]
        ln_d = np.log(df_valid['abertura'].values)
        ln_ln_R = np.log(-np.log(df_valid['R_d'].values / 100))

        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(ln_d, ln_ln_R)

        n = slope  # Parámetro de distribución
        d0 = np.exp(-intercept / slope)  # Tamaño característico donde 36.8% son más grandes
        r2 = r_value ** 2

        # Datos para la tabla de logaritmos
        tabla_logaritmos = []
        for i, row in df_valid.iterrows():
            ln_d_val = np.log(row['abertura'])
            ln_ln_R_val = np.log(-np.log(row['R_d'] / 100))
            tabla_logaritmos.append({
                'abertura': row['abertura'],
                'R_d': row['R_d'],
                'ln_d': ln_d_val,
                'ln_ln_R': ln_ln_R_val
            })

        resultados = {
            'n': n,
            'd0': d0,
            'r2': r2,
            'ecuacion': f'ln[-ln(R(d)/100)] = {n:.3f} × ln(d) - {n:.3f} × ln({d0:.3f})',
            'formula_rosin': f'R(d) = 100 × e^(-(d/{d0:.3f})^{n:.3f})',
            'tabla_logaritmos': tabla_logaritmos
        }

        return resultados

    except Exception as e:
        print(f"Error en cálculo de parámetros Rosin-Rammler: {e}")
        return None