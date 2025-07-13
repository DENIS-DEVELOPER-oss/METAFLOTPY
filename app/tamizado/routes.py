from flask import Blueprint, render_template, request, flash
from app.tamizado.forms import FormularioTamizado, FormularioRegresionLineal, FormularioRosinRammler, FormularioTamizadoDinamico
import plotly.graph_objs as go
import plotly.utils
import json
import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import math

bp_tamizado = Blueprint('tamizado', __name__)

@bp_tamizado.route('/')
def analisis_granulometrico():
    """Página principal del módulo de análisis de tamaño de partícula"""
    return render_template('tamizado/index.html')

@bp_tamizado.route('/tamizado-dinamico', methods=['GET', 'POST'])
def tamizado_dinamico():
    """Análisis granulométrico con mallas dinámicas personalizables"""
    formulario = FormularioTamizadoDinamico()
    resultados = None
    grafico_json = None

    if formulario.validate_on_submit():
        try:
            # Procesar datos de mallas desde JSON
            import json
            mallas_data = json.loads(formulario.mallas_data.data or '[]')
            peso_total = formulario.peso_total.data
            
            if not mallas_data:
                flash('Debe agregar al menos una malla para realizar el análisis', 'error')
                return render_template('tamizado/tamizado_dinamico.html', formulario=formulario)

            # Ordenar mallas por abertura (descendente)
            mallas_data.sort(key=lambda x: float(x.get('abertura', 0)), reverse=True)
            
            # Extraer datos para el cálculo
            aberturas = [float(m['abertura']) for m in mallas_data]
            retenidos = [float(m.get('peso_retenido', 0)) for m in mallas_data]
            nombres = [m['nombre'] for m in mallas_data]

            # Calcular análisis granulométrico dinámico
            resultados = calcular_analisis_granulometrico_dinamico(peso_total, aberturas, retenidos, nombres)

            # Crear gráfico
            grafico_json = crear_grafico_granulometrico(resultados)

        except Exception as e:
            flash(f'Error en el cálculo: {str(e)}', 'error')

    return render_template('tamizado/tamizado_dinamico.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

@bp_tamizado.route('/gates-gaudin-schuhmann', methods=['GET', 'POST'])
def gates_gaudin_schuhmann():
    formulario = FormularioTamizado()
    resultados = None
    grafico_json = None

    if formulario.validate_on_submit():
        try:
            # Obtener datos del formulario
            peso_total = formulario.peso_total.data
            retenidos = [
                formulario.retenido_12_5.data or 0,
                formulario.retenido_9_5.data or 0,
                formulario.retenido_6_35.data or 0,
                formulario.retenido_4_75.data or 0,
                formulario.retenido_3_35.data or 0,
                formulario.retenido_2_36.data or 0,
                formulario.retenido_1_18.data or 0,
                formulario.retenido_0_85.data or 0,
                formulario.retenido_0_60.data or 0,
                formulario.retenido_0_425.data or 0,
                formulario.retenido_0_30.data or 0,
                formulario.retenido_0_212.data or 0,
                formulario.retenido_0_150.data or 0,
                formulario.retenido_0_106.data or 0,
                formulario.retenido_0_075.data or 0,
                formulario.retenido_fondo.data or 0
            ]

            # Calcular análisis granulométrico
            resultados = calcular_analisis_granulometrico(peso_total, retenidos)

            # Crear gráfico
            grafico_json = crear_grafico_granulometrico(resultados)

        except Exception as e:
            flash(f'Error en el cálculo: {str(e)}', 'error')

    return render_template('tamizado/gates_gaudin_schuhmann.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

@bp_tamizado.route('/regresion-lineal', methods=['GET', 'POST'])
def regresion_lineal():
    formulario = FormularioRegresionLineal()
    resultados = None
    grafico_json = None

    if formulario.validate_on_submit():
        try:
            # Obtener datos del formulario
            mallas = [
                12.5, 9.5, 6.35, 4.75, 3.35, 2.36, 1.18, 0.85, 
                0.60, 0.425, 0.30, 0.212, 0.150, 0.106, 0.075, 0.053
            ]

            pasantes = [
                formulario.pasante_12_5.data or 0,
                formulario.pasante_9_5.data or 0,
                formulario.pasante_6_35.data or 0,
                formulario.pasante_4_75.data or 0,
                formulario.pasante_3_35.data or 0,
                formulario.pasante_2_36.data or 0,
                formulario.pasante_1_18.data or 0,
                formulario.pasante_0_85.data or 0,
                formulario.pasante_0_60.data or 0,
                formulario.pasante_0_425.data or 0,
                formulario.pasante_0_30.data or 0,
                formulario.pasante_0_212.data or 0,
                formulario.pasante_0_150.data or 0,
                formulario.pasante_0_106.data or 0,
                formulario.pasante_0_075.data or 0,
                formulario.pasante_fondo.data or 0
            ]

            # Filtrar datos válidos
            datos_validos = [(m, p) for m, p in zip(mallas, pasantes) if p > 0]

            if len(datos_validos) < 3:
                flash('Se necesitan al menos 3 puntos válidos para realizar la regresión', 'error')
                return render_template('tamizado/regresion_lineal.html', formulario=formulario)

            # Calcular regresión lineal
            resultados = calcular_regresion_lineal(datos_validos)
            grafico_json = crear_grafico_regresion(datos_validos, resultados)

        except Exception as e:
            flash(f'Error en el cálculo: {str(e)}', 'error')

    return render_template('tamizado/regresion_lineal.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

@bp_tamizado.route('/rosin-rammler', methods=['GET', 'POST'])
def rosin_rammler():
    formulario = FormularioRosinRammler()
    resultados = None
    grafico_json = None

    if formulario.validate_on_submit():
        try:
            # Obtener datos del formulario
            mallas = [
                12.5, 9.5, 6.35, 4.75, 3.35, 2.36, 1.18, 0.85, 
                0.60, 0.425, 0.30, 0.212, 0.150, 0.106, 0.075, 0.053
            ]

            pasantes = [
                formulario.pasante_12_5.data or 0,
                formulario.pasante_9_5.data or 0,
                formulario.pasante_6_35.data or 0,
                formulario.pasante_4_75.data or 0,
                formulario.pasante_3_35.data or 0,
                formulario.pasante_2_36.data or 0,
                formulario.pasante_1_18.data or 0,
                formulario.pasante_0_85.data or 0,
                formulario.pasante_0_60.data or 0,
                formulario.pasante_0_425.data or 0,
                formulario.pasante_0_30.data or 0,
                formulario.pasante_0_212.data or 0,
                formulario.pasante_0_150.data or 0,
                formulario.pasante_0_106.data or 0,
                formulario.pasante_0_075.data or 0,
                formulario.pasante_fondo.data or 0
            ]

            # Filtrar datos válidos
            datos_validos = [(m, p) for m, p in zip(mallas, pasantes) if p > 0 and p < 100]

            if len(datos_validos) < 4:
                flash('Se necesitan al menos 4 puntos válidos para el ajuste Rosin-Rammler', 'error')
                return render_template('tamizado/rosin_rammler.html', formulario=formulario)

            # Calcular parámetros Rosin-Rammler
            resultados = calcular_rosin_rammler(datos_validos)
            grafico_json = crear_grafico_rosin_rammler(datos_validos, resultados)

        except Exception as e:
            flash(f'Error en el cálculo: {str(e)}', 'error')

    return render_template('tamizado/rosin_rammler.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

def calcular_analisis_granulometrico_dinamico(peso_total, aberturas, retenidos, nombres):
    """Calcular análisis granulométrico con mallas dinámicas"""
    
    # Calcular porcentajes retenidos
    suma_retenidos = sum(retenidos)
    porcentaje_retenido = [(r/peso_total)*100 for r in retenidos]

    # Calcular porcentajes retenidos acumulados
    retenido_acumulado = []
    acum = 0
    for p in porcentaje_retenido:
        acum += p
        retenido_acumulado.append(acum)

    # Calcular porcentajes pasantes
    pasante = [100 - r for r in retenido_acumulado]

    # Crear tabla de resultados
    tabla_resultados = []
    for i in range(len(aberturas)):
        tabla_resultados.append({
            'nombre': nombres[i],
            'malla': aberturas[i],
            'peso_retenido': retenidos[i],
            'porcentaje_retenido': round(porcentaje_retenido[i], 2),
            'retenido_acumulado': round(retenido_acumulado[i], 2),
            'pasante': round(pasante[i], 2)
        })

    # Calcular parámetros característicos usando las aberturas dinámicas
    d50 = calcular_percentil(aberturas, pasante, 50)
    d80 = calcular_percentil(aberturas, pasante, 80)
    d10 = calcular_percentil(aberturas, pasante, 10)
    d60 = calcular_percentil(aberturas, pasante, 60)
    d30 = calcular_percentil(aberturas, pasante, 30)

    # Coeficientes
    cu = d60 / d10 if d10 > 0 else 0
    cc = (d30**2) / (d60 * d10) if (d60 > 0 and d10 > 0) else 0

    # Verificación del balance
    balance_ok = abs(suma_retenidos - peso_total) < 0.01

    return {
        'tabla': tabla_resultados,
        'peso_total': peso_total,
        'suma_retenidos': suma_retenidos,
        'balance_ok': balance_ok,
        'error_balance': abs(suma_retenidos - peso_total),
        'd10': round(d10, 3),
        'd30': round(d30, 3),
        'd50': round(d50, 3),
        'd60': round(d60, 3),
        'd80': round(d80, 3),
        'cu': round(cu, 2),
        'cc': round(cc, 2),
        'mallas': aberturas,
        'pasante': pasante,
        'nombres': nombres
    }

def calcular_analisis_granulometrico(peso_total, retenidos):
    """Calcular análisis granulométrico completo"""

    # Mallas estándar ASTM
    mallas = [
        12.5, 9.5, 6.35, 4.75, 3.35, 2.36, 1.18, 0.85, 
        0.60, 0.425, 0.30, 0.212, 0.150, 0.106, 0.075, 0.053
    ]

    # Calcular porcentajes retenidos
    suma_retenidos = sum(retenidos)
    porcentaje_retenido = [(r/peso_total)*100 for r in retenidos]

    # Calcular porcentajes retenidos acumulados
    retenido_acumulado = []
    acum = 0
    for p in porcentaje_retenido:
        acum += p
        retenido_acumulado.append(acum)

    # Calcular porcentajes pasantes
    pasante = [100 - r for r in retenido_acumulado]

    # Crear tabla de resultados
    tabla_resultados = []
    for i in range(len(mallas)):
        tabla_resultados.append({
            'malla': mallas[i],
            'peso_retenido': retenidos[i],
            'porcentaje_retenido': round(porcentaje_retenido[i], 2),
            'retenido_acumulado': round(retenido_acumulado[i], 2),
            'pasante': round(pasante[i], 2)
        })

    # Calcular parámetros característicos
    # D50 (mediana)
    d50 = calcular_percentil(mallas, pasante, 50)
    # D80 (tamaño al 80% pasante)
    d80 = calcular_percentil(mallas, pasante, 80)
    # D10 (tamaño al 10% pasante)
    d10 = calcular_percentil(mallas, pasante, 10)

    # Coeficiente de uniformidad
    cu = d60 / d10 if d10 > 0 else 0
    d60 = calcular_percentil(mallas, pasante, 60)

    # Coeficiente de curvatura
    d30 = calcular_percentil(mallas, pasante, 30)
    cc = (d30**2) / (d60 * d10) if (d60 > 0 and d10 > 0) else 0

    # Verificación del balance
    balance_ok = abs(suma_retenidos - peso_total) < 0.01

    return {
        'tabla': tabla_resultados,
        'peso_total': peso_total,
        'suma_retenidos': suma_retenidos,
        'balance_ok': balance_ok,
        'error_balance': abs(suma_retenidos - peso_total),
        'd10': round(d10, 3),
        'd30': round(d30, 3),
        'd50': round(d50, 3),
        'd60': round(d60, 3),
        'd80': round(d80, 3),
        'cu': round(cu, 2),
        'cc': round(cc, 2),
        'mallas': mallas,
        'pasante': pasante
    }

def calcular_percentil(mallas, pasantes, percentil):
    """Calcular percentil usando interpolación lineal"""
    for i in range(len(pasantes)-1):
        if pasantes[i] >= percentil >= pasantes[i+1]:
            # Interpolación lineal
            x1, y1 = math.log10(mallas[i]), pasantes[i]
            x2, y2 = math.log10(mallas[i+1]), pasantes[i+1]

            if y1 != y2:
                x = x1 + (percentil - y1) * (x2 - x1) / (y2 - y1)
                return 10**x

    return 0

def calcular_regresion_lineal(datos):
    """Calcular regresión lineal en escala log-log"""
    mallas = [d[0] for d in datos]
    pasantes = [d[1] for d in datos]

    # Transformar a escala logarítmica
    log_mallas = [math.log10(m) for m in mallas]
    log_pasantes = [math.log10(p) for p in pasantes if p > 0]
    log_mallas_validas = [log_mallas[i] for i, p in enumerate(pasantes) if p > 0]

    # Calcular regresión lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_mallas_validas, log_pasantes)

    # Calcular R²
    r_squared = r_value**2

    # Generar puntos para la línea de regresión
    x_pred = np.linspace(min(log_mallas_validas), max(log_mallas_validas), 100)
    y_pred = slope * x_pred + intercept

    # Convertir de vuelta a escala normal
    mallas_pred = [10**x for x in x_pred]
    pasantes_pred = [10**y for y in y_pred]

    return {
        'pendiente': round(slope, 4),
        'intercepto': round(intercept, 4),
        'r_cuadrado': round(r_squared, 4),
        'correlacion': round(r_value, 4),
        'p_value': round(p_value, 6),
        'error_estandar': round(std_err, 4),
        'ecuacion': f'log(Y) = {slope:.4f} × log(X) + {intercept:.4f}',
        'mallas_pred': mallas_pred,
        'pasantes_pred': pasantes_pred,
        'datos_originales': datos
    }

def calcular_rosin_rammler(datos):
    """Calcular parámetros de la distribución Rosin-Rammler"""
    mallas = np.array([d[0] for d in datos])
    pasantes = np.array([d[1] for d in datos])

    # La ecuación de Rosin-Rammler: Y = 100 * exp(-(x/x0)^n)
    # Donde Y = % pasante, x = tamaño de partícula, x0 = tamaño característico, n = módulo de uniformidad

    # Transformación: ln(ln(100/Y)) = n*ln(x) - n*ln(x0)
    # Filtrar datos válidos (evitar log(0))
    datos_validos = [(m, p) for m, p in zip(mallas, pasantes) if 0 < p < 100]

    if len(datos_validos) < 4:
        raise ValueError("Se necesitan al menos 4 puntos válidos para el ajuste Rosin-Rammler")

    mallas_validas = np.array([d[0] for d in datos_validos])
    pasantes_validas = np.array([d[1] for d in datos_validos])

    # Transformación de Rosin-Rammler
    try:
        y_transform = np.log(np.log(100.0 / pasantes_validas))
        x_transform = np.log(mallas_validas)

        # Regresión lineal en coordenadas transformadas
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_transform, y_transform)

        # Parámetros Rosin-Rammler
        n = slope  # Módulo de uniformidad
        x0 = np.exp(-intercept / slope)  # Tamaño característico

        # Calcular R²
        r_squared = r_value**2

        # Generar curva ajustada
        x_pred = np.linspace(min(mallas_validas), max(mallas_validas), 100)
        y_pred = 100 * np.exp(-(x_pred / x0)**n)

        # Calcular percentiles importantes
        d50 = x0 * (np.log(2))**(1/n)  # Mediana
        d80 = x0 * (np.log(5))**(1/n)  # D80
        d10 = x0 * (np.log(100/90))**(1/n)  # D10

        return {
            'n': round(n, 4),
            'x0': round(x0, 4),
            'r_cuadrado': round(r_squared, 4),
            'correlacion': round(r_value, 4),
            'ecuacion': f'Y = 100 × exp(-({x0:.3f}/x)^{n:.3f})',
            'd10': round(d10, 3),
            'd50': round(d50, 3),
            'd80': round(d80, 3),
            'mallas_pred': x_pred.tolist(),
            'pasantes_pred': y_pred.tolist(),
            'datos_originales': datos_validos,
            'interpretacion': {
                'uniformidad': 'Alta uniformidad' if n > 3 else 'Baja uniformidad' if n < 1.5 else 'Uniformidad moderada',
                'distribucion': f'El tamaño característico es {x0:.3f} mm',
                'ajuste': 'Excelente ajuste' if r_squared > 0.95 else 'Buen ajuste' if r_squared > 0.90 else 'Ajuste aceptable'
            }
        }

    except Exception as e:
        raise ValueError(f"Error en el cálculo Rosin-Rammler: {str(e)}")

def crear_grafico_granulometrico(resultados):
    """Crear gráfico de curva granulométrica"""
    fig = go.Figure()

    # Curva granulométrica (% pasante vs tamaño)
    fig.add_trace(go.Scatter(
        x=resultados['mallas'],
        y=resultados['pasante'],
        mode='lines+markers',
        name='Curva Granulométrica',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))

    # Líneas de percentiles importantes
    percentiles = [
        (resultados['d10'], 10, 'D10'),
        (resultados['d50'], 50, 'D50'),
        (resultados['d80'], 80, 'D80')
    ]

    for d_val, perc, label in percentiles:
        if d_val > 0:
            fig.add_vline(
                x=d_val, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"{label}={d_val:.3f}mm"
            )
            fig.add_hline(
                y=perc, 
                line_dash="dash", 
                line_color="red"
            )

    fig.update_layout(
        title='Curva Granulométrica',
        xaxis_title='Tamaño de Partícula (mm)',
        yaxis_title='Porcentaje Pasante (%)',
        xaxis_type='log',
        height=500,
        showlegend=True,
        template='plotly_white'
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_regresion(datos, resultados):
    """Crear gráfico de regresión lineal"""
    fig = go.Figure()

    # Datos originales
    mallas_orig = [d[0] for d in datos]
    pasantes_orig = [d[1] for d in datos]

    fig.add_trace(go.Scatter(
        x=mallas_orig,
        y=pasantes_orig,
        mode='markers',
        name='Datos Experimentales',
        marker=dict(size=8, color='blue')
    ))

    # Línea de regresión
    fig.add_trace(go.Scatter(
        x=resultados['mallas_pred'],
        y=resultados['pasantes_pred'],
        mode='lines',
        name=f'Regresión (R²={resultados["r_cuadrado"]:.4f})',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        title='Regresión Lineal - Escala Log-Log',
        xaxis_title='Tamaño de Partícula (mm)',
        yaxis_title='Porcentaje Pasante (%)',
        xaxis_type='log',
        yaxis_type='log',
        height=500,
        showlegend=True,
        template='plotly_white'
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_rosin_rammler(datos, resultados):
    """Crear gráfico de ajuste Rosin-Rammler"""
    fig = go.Figure()

    # Datos originales
    mallas_orig = [d[0] for d in datos]
    pasantes_orig = [d[1] for d in datos]

    fig.add_trace(go.Scatter(
        x=mallas_orig,
        y=pasantes_orig,
        mode='markers',
        name='Datos Experimentales',
        marker=dict(size=8, color='blue')
    ))

    # Curva ajustada Rosin-Rammler
    fig.add_trace(go.Scatter(
        x=resultados['mallas_pred'],
        y=resultados['pasantes_pred'],
        mode='lines',
        name=f'Rosin-Rammler (R²={resultados["r_cuadrado"]:.4f})',
        line=dict(color='red', width=2)
    ))

    # Líneas de percentiles
    percentiles = [
        (resultados['d10'], 10, 'D10'),
        (resultados['d50'], 50, 'D50'),
        (resultados['d80'], 80, 'D80')
    ]

    for d_val, perc, label in percentiles:
        fig.add_vline(
            x=d_val, 
            line_dash="dash", 
            line_color="gray",
            annotation_text=f"{label}={d_val:.3f}mm"
        )

    fig.update_layout(
        title='Distribución Rosin-Rammler',
        xaxis_title='Tamaño de Partícula (mm)',
        yaxis_title='Porcentaje Pasante (%)',
        xaxis_type='log',
        height=500,
        showlegend=True,
        template='plotly_white'
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)