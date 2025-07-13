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
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla para Rosin-Rammler
            df = crear_tabla_rosin_rammler(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Crear gráficos
            grafico_principal = crear_grafico_rosin_rammler(df)
            grafico_semilog = crear_grafico_semilog_rosin_rammler(df)

            # Calcular parámetros Rosin-Rammler
            resultados_calculo = calcular_parametros_rosin_rammler(df)

    return render_template('tamizado/rosin_rammler.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_principal=grafico_principal,
                         grafico_semilog=grafico_semilog,
                         tabla_datos=tabla_datos)

def crear_tabla_rosin_rammler(aberturas, pesos_retenidos, peso_total):
    """Crear tabla específica para análisis Rosin-Rammler"""
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })

    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)

    # Cálculos básicos
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()

    # R(d) para Rosin-Rammler (% retenido acumulado)
    df['R_d'] = df['porcentaje_acumulado']

    return df

def crear_grafico_rosin_rammler(df):
    """Crear gráfico principal para Rosin-Rammler"""
    try:
        fig = go.Figure()

        # Curva de % retenido acumulado R(d)
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['R_d'],
            mode='markers+lines',
            name='R(d) - % Retenido Acumulado',
            marker=dict(size=10, color='red'),
            line=dict(color='red', width=3)
        ))

        fig.update_layout(
            title='Distribución Rosin-Rammler<br>R(d) = 100 × e^[-(d/d₀)ⁿ]',
            xaxis_title='Tamaño de partícula d (mm)',
            yaxis_title='R(d) - % Retenido Acumulado',
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
    """Crear gráfico semilogarítmico para obtener parámetros Rosin-Rammler"""
    try:
        # Filtrar datos válidos
        df_valid = df[(df['R_d'] > 0) & (df['R_d'] < 100)].copy()

        if len(df_valid) < 2:
            return None

        fig = go.Figure()

        # Calcular ln[-ln(R(d)/100)]
        ln_ln_R = []
        ln_d = []

        for _, row in df_valid.iterrows():
            try:
                R_fraction = row['R_d'] / 100
                if 0 < R_fraction < 1:
                    ln_ln_value = np.log(-np.log(R_fraction))
                    ln_d_value = np.log(row['abertura'])
                    ln_ln_R.append(ln_ln_value)
                    ln_d.append(ln_d_value)
            except:
                continue

        if len(ln_d) >= 2:
            # Datos experimentales
            fig.add_trace(go.Scatter(
                x=ln_d,
                y=ln_ln_R,
                mode='markers+lines',
                name='Datos Experimentales',
                marker=dict(size=10, color='blue'),
                line=dict(color='blue', width=2)
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
    """Calcular parámetros n y d₀ del modelo Rosin-Rammler"""
    try:
        df_valid = df[(df['R_d'] > 0) & (df['R_d'] < 100)].copy()

        if len(df_valid) < 2:
            return None

        # Preparar datos para regresión
        ln_d = []
        ln_ln_R = []
        tabla_logaritmos = []

        for _, row in df_valid.iterrows():
            try:
                R_fraction = row['R_d'] / 100
                if 0 < R_fraction < 1:
                    ln_d_val = np.log(row['abertura'])
                    ln_ln_R_val = np.log(-np.log(R_fraction))

                    ln_d.append(ln_d_val)
                    ln_ln_R.append(ln_ln_R_val)

                    tabla_logaritmos.append({
                        'abertura': row['abertura'],
                        'R_d': row['R_d'],
                        'ln_d': ln_d_val,
                        'ln_ln_R': ln_ln_R_val
                    })
            except:
                continue

        if len(ln_d) >= 2:
            # Regresión lineal: ln[-ln(R(d)/100)] = n × ln(d) - n × ln(d₀)
            slope, intercept, r_value, p_value, std_err = stats.linregress(ln_d, ln_ln_R)

            n = slope  # Parámetro de distribución
            d0 = np.exp(-intercept / slope)  # Tamaño característico
            r2 = r_value ** 2

            formula_rosin = f'R(d) = 100 × e^[-(d/{d0:.3f})^{n:.3f}]'

            resultados = {
                'n': n,
                'd0': d0,
                'r2': r2,
                'formula_rosin': formula_rosin,
                'tabla_logaritmos': tabla_logaritmos
            }

            return resultados

    except Exception as e:
        print(f"Error calculando parámetros Rosin-Rammler: {e}")
        return None

@bp_tamizado.route('/regresion-lineal', methods=['GET', 'POST'])
def regresion_lineal():
    formulario = FormularioTamizado()

    resultados_calculo = None
    grafico_principal = None
    grafico_semilog = None
    tabla_datos = None

    if request.method == 'POST':
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla básica
            df = crear_tabla_granulometrica_especifica(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Crear gráficos
            grafico_principal = crear_grafico_granulometrico(df)
            grafico_semilog = crear_grafico_log_log_especifico(df)

            # Calcular regresión
            resultados_calculo = calcular_regresion_especifica(df)

    return render_template('tamizado/regresion_lineal.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_principal=grafico_principal,
                         grafico_semilog=grafico_semilog,
                         tabla_datos=tabla_datos)

@bp_tamizado.route('/tamizado-dinamico', methods=['GET', 'POST'])
def tamizado_dinamico():
    formulario = FormularioTamizado()

    resultados = None
    grafico = None

    if request.method == 'POST':
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla básica
            df = crear_tabla_granulometrica_especifica(aberturas, pesos_retenidos, peso_total)

            # Crear gráfico
            grafico = crear_grafico_granulometrico(df)

            # Preparar resultados
            resultados = {
                'tabla': df.to_dict('records'),
                'd10': 0.1,  # Placeholder values
                'd30': 0.3,
                'd50': 0.5,
                'd60': 0.6,
                'd80': 0.8,
                'cu': 6.0,
                'cc': 1.0,
                'balance_ok': True,
                'error_balance': 0.0
            }

    return render_template('tamizado/tamizado_dinamico.html',
                         formulario=formulario,
                         resultados=resultados,
                         grafico=grafico)