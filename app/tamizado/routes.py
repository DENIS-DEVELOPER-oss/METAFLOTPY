
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
def index():
    """Página principal del módulo tamizado"""
    return render_template('tamizado/index.html')

@bp_tamizado.route('/analisis', methods=['GET', 'POST'])
def analisis_granulometrico():
    """Análisis Gates-Gaudin-Schuhmann"""
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

@bp_tamizado.route('/rosin-rammler', methods=['GET', 'POST'])
def rosin_rammler():
    """Análisis Rosin-Rammler"""
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

@bp_tamizado.route('/regresion-lineal', methods=['GET', 'POST'])
def regresion_lineal():
    """Regresión Lineal Empírica"""
    formulario = FormularioTamizado()
    
    resultados_calculo = None
    grafico_principal = None
    grafico_regresion = None
    tabla_datos = None

    if request.method == 'POST':
        peso_total = float(request.form.get('peso_total', 0))
        aberturas = [float(x) for x in request.form.getlist('abertura[]') if x]
        pesos_retenidos = [float(x) for x in request.form.getlist('peso_retenido[]') if x]

        if len(aberturas) == len(pesos_retenidos) and len(aberturas) > 0:
            # Crear tabla para regresión lineal
            df = crear_tabla_regresion_lineal(aberturas, pesos_retenidos, peso_total)
            tabla_datos = df.to_dict('records')

            # Crear gráficos
            grafico_principal = crear_grafico_regresion_lineal(df)
            grafico_regresion = crear_grafico_dispersión_regresion(df)

            # Calcular regresión lineal empírica
            resultados_calculo = calcular_regresion_lineal_empirica(df)

    return render_template('tamizado/regresion_lineal.html',
                         formulario=formulario,
                         resultados_calculo=resultados_calculo,
                         grafico_principal=grafico_principal,
                         grafico_regresion=grafico_regresion,
                         tabla_datos=tabla_datos)

# Funciones auxiliares para cálculos
def crear_tabla_granulometrica_especifica(aberturas, pesos_retenidos, peso_total):
    """Crear tabla con cálculos según las fórmulas especificadas"""
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })

    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)

    # Cálculos básicos
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()
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
    """Crear gráfico log-log para obtener n"""
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
    """Calcular regresión lineal según especificación"""
    try:
        # Filtrar datos válidos para logaritmos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] < 100)].copy()

        if len(df_valid) < 2:
            return None

        # Logaritmos para graficar y obtener n
        log_di = np.log10(df_valid['abertura'].values)
        log_Pi = np.log10(df_valid['porcentaje_pasante'].values)

        # Regresión lineal: log(%Pi) = n × log(di)
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

# Funciones Rosin-Rammler
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

# Funciones Regresión Lineal
def crear_tabla_regresion_lineal(aberturas, pesos_retenidos, peso_total):
    """Crear tabla para análisis de regresión lineal empírica"""
    df = pd.DataFrame({
        'abertura': aberturas,
        'peso_retenido': pesos_retenidos
    })
    
    # Ordenar por abertura descendente
    df = df.sort_values('abertura', ascending=False).reset_index(drop=True)
    
    # Cálculos básicos
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100
    df['porcentaje_acumulado'] = df['porcentaje_retenido'].cumsum()
    df['porcentaje_pasante'] = 100 - df['porcentaje_acumulado']
    
    # Para regresión lineal empírica
    df['log_d'] = np.log10(df['abertura'])  # log(d) en base 10
    
    return df

def crear_grafico_regresion_lineal(df):
    """Crear gráfico principal de distribución granulométrica"""
    try:
        fig = go.Figure()

        # Curva de % pasante
        fig.add_trace(go.Scatter(
            x=df['abertura'],
            y=df['porcentaje_pasante'],
            mode='markers+lines',
            name='% Acumulado Pasante',
            marker=dict(size=10, color='blue'),
            line=dict(color='blue', width=3)
        ))

        fig.update_layout(
            title='Distribución Granulométrica<br>Datos para Regresión Lineal Empírica',
            xaxis_title='Tamaño de partícula d (mm)',
            yaxis_title='% Acumulado Pasante',
            xaxis_type='log',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico regresión lineal: {e}")
        return None

def crear_grafico_dispersión_regresion(df):
    """Crear gráfico de dispersión con línea de tendencia"""
    try:
        # Filtrar datos válidos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] <= 100)].copy()
        
        if len(df_valid) < 2:
            return None

        fig = go.Figure()

        # Datos experimentales (puntos de dispersión)
        fig.add_trace(go.Scatter(
            x=df_valid['log_d'],
            y=df_valid['porcentaje_pasante'],
            mode='markers',
            name='Datos Experimentales',
            marker=dict(size=12, color='red', symbol='circle'),
            text=[f'd={row["abertura"]:.3f}mm<br>%P={row["porcentaje_pasante"]:.2f}%' 
                  for _, row in df_valid.iterrows()],
            hovertemplate='<b>%{text}</b><br>log(d)=%{x:.3f}<br>%Pasante=%{y:.2f}%<extra></extra>'
        ))

        # Calcular línea de regresión
        if len(df_valid) >= 2:
            x_data = df_valid['log_d'].values
            y_data = df_valid['porcentaje_pasante'].values
            
            # Regresión lineal
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
            
            # Línea de regresión
            x_line = np.linspace(x_data.min(), x_data.max(), 100)
            y_line = slope * x_line + intercept
            
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=f'Línea de Regresión (R²={r_value**2:.4f})',
                line=dict(color='blue', width=3, dash='dash')
            ))

        fig.update_layout(
            title='Diagrama de Dispersión con Línea de Tendencia<br>y = a × log(d) + b',
            xaxis_title='log(d) - Logaritmo del tamaño',
            yaxis_title='% Acumulado Pasante',
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            hovermode='closest',
            template='plotly_white'
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print(f"Error creando gráfico dispersión: {e}")
        return None

def calcular_regresion_lineal_empirica(df):
    """Calcular regresión lineal empírica usando mínimos cuadrados"""
    try:
        # Filtrar datos válidos
        df_valid = df[(df['porcentaje_pasante'] > 0) & (df['porcentaje_pasante'] <= 100)].copy()
        
        if len(df_valid) < 2:
            return None

        # Datos para regresión: x = log(d), y = %Pasante
        x_data = df_valid['log_d'].values  # log(d)
        y_data = df_valid['porcentaje_pasante'].values  # %Pasante
        
        n = len(x_data)
        
        # Cálculos usando método de mínimos cuadrados
        sum_x = np.sum(x_data)
        sum_y = np.sum(y_data)
        sum_xy = np.sum(x_data * y_data)
        sum_x2 = np.sum(x_data ** 2)
        
        # Calcular pendiente (a) e intersección (b)
        a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        b = (sum_y - a * sum_x) / n
        
        # Calcular coeficiente de determinación R²
        y_pred = a * x_data + b
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Tabla de datos para mostrar
        tabla_regresion = []
        for i, row in df_valid.iterrows():
            y_calculado = a * row['log_d'] + b
            tabla_regresion.append({
                'abertura': row['abertura'],
                'porcentaje_pasante': row['porcentaje_pasante'],
                'log_d': row['log_d'],
                'y_calculado': y_calculado,
                'residuo': row['porcentaje_pasante'] - y_calculado
            })
        
        resultados = {
            'a': a,  # pendiente
            'b': b,  # intersección
            'r2': r2,  # coeficiente de determinación
            'ecuacion': f'y = {a:.4f} × log(d) + {b:.4f}',
            'n_datos': n,
            'sum_x': sum_x,
            'sum_y': sum_y,
            'sum_xy': sum_xy,
            'sum_x2': sum_x2,
            'tabla_regresion': tabla_regresion,
            'formula_minimos_cuadrados': {
                'a_formula': f'a = (n∑xy - ∑x∑y) / (n∑x² - (∑x)²)',
                'b_formula': f'b = (∑y - a∑x) / n',
                'valores': {
                    'n': n,
                    'sum_xy': sum_xy,
                    'sum_x': sum_x,
                    'sum_y': sum_y,
                    'sum_x2': sum_x2
                }
            }
        }
        
        return resultados

    except Exception as e:
        print(f"Error en cálculo de regresión lineal empírica: {e}")
        return None
