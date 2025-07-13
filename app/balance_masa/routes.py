
from flask import Blueprint, render_template
from app.balance_masa.forms import FormularioBalanceMasa
import plotly.graph_objs as go
import plotly.utils
import json

bp_balance_masa = Blueprint('balance_masa', __name__)

@bp_balance_masa.route('/', methods=['GET', 'POST'])
def balance_masa():
    formulario = FormularioBalanceMasa()
    resultados = None
    graficos = {}
    
    if formulario.validate_on_submit():
        resultados = calcular_balance_masa(formulario)
        if resultados:
            graficos['flujos'] = crear_diagrama_flujo(resultados)
            graficos['eficiencias'] = crear_grafico_eficiencias(resultados)
            graficos['distribucion'] = crear_grafico_distribucion(resultados)
    
    return render_template('balance_masa/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         graficos=graficos)

def calcular_balance_masa(formulario):
    tipo_circuito = formulario.tipo_circuito.data
    
    if tipo_circuito == 'directo':
        return calcular_circuito_directo(formulario)
    elif tipo_circuito == 'inverso':
        return calcular_circuito_inverso(formulario)
    elif tipo_circuito == 'sabc1':
        return calcular_circuito_sabc1(formulario)
    elif tipo_circuito == 'sabc2':
        return calcular_circuito_sabc2(formulario)
    
    return None

def calcular_circuito_directo(formulario):
    """Circuito Cerrado Directo: F = P + R"""
    # Obtener valores del formulario
    f = formulario.f_alimentacion.data or 0
    p = formulario.p_producto.data or 0
    r = formulario.r_rechazo.data or 0
    
    # Contar cuántos valores se han ingresado
    valores_ingresados = sum([1 for x in [f, p, r] if x > 0])
    
    # Si se tienen al menos 2 valores, calcular el tercero
    if valores_ingresados >= 2:
        if f > 0 and p > 0 and r == 0:
            r = f - p
        elif f > 0 and r > 0 and p == 0:
            p = f - r
        elif p > 0 and r > 0 and f == 0:
            f = p + r
    else:
        # Usar valores ejemplo si no hay suficientes datos
        f = f or 100.0
        p = p or 80.0
        r = f - p
    
    # Validar que los valores sean positivos
    f = max(0, f)
    p = max(0, p)
    r = max(0, r)
    
    # Calcular carga circulante CC = (R/P) * 100
    carga_circulante_pct = (r / p) * 100 if p > 0 else 0
    
    # Verificar balance F = P + R
    balance_verificado = abs(f - (p + r)) < 0.1
    
    return {
        'tipo_circuito': 'directo',
        'f_alimentacion': round(f, 2),
        'p_producto': round(p, 2),
        'r_rechazo': round(r, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': balance_verificado
    }

def calcular_circuito_inverso(formulario):
    """Circuito Cerrado Inverso: F + R = P"""
    # Obtener valores del formulario
    f = formulario.f_alimentacion_inv.data or 0
    r = formulario.r_rechazo_inv.data or 0
    p = formulario.p_producto_inv.data or 0
    
    # Contar cuántos valores se han ingresado
    valores_ingresados = sum([1 for x in [f, r, p] if x > 0])
    
    # Si se tienen al menos 2 valores, calcular el tercero
    if valores_ingresados >= 2:
        if f > 0 and r > 0 and p == 0:
            p = f + r
        elif f > 0 and p > 0 and r == 0:
            r = p - f
        elif r > 0 and p > 0 and f == 0:
            f = p - r
    else:
        # Usar valores ejemplo si no hay suficientes datos
        f = f or 100.0
        r = r or 20.0
        p = f + r
    
    # Validar que los valores sean positivos
    f = max(0, f)
    r = max(0, r)
    p = max(0, p)
    
    # Calcular carga circulante CC = (R/F) * 100
    carga_circulante_pct = (r / f) * 100 if f > 0 else 0
    
    # Verificar balance F + R = P
    balance_verificado = abs((f + r) - p) < 0.1
    
    return {
        'tipo_circuito': 'inverso',
        'f_alimentacion': round(f, 2),
        'r_rechazo': round(r, 2),
        'p_producto': round(p, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': balance_verificado
    }

def calcular_circuito_sabc1(formulario):
    """Circuito SABC-1: Balance global F = P + R, Sub-balance SAG F = S, Sub-balance molino bolas S + R = B y B = P + R"""
    # Obtener valores del formulario
    f = formulario.f_mineral_sabc1.data or 100.0
    s = formulario.s_producto_sag.data or 0
    b = formulario.b_producto_bolas.data or 0
    p = formulario.p_producto_final_sabc1.data or 0
    r = formulario.r_carga_circulante_sabc1.data or 0
    
    # Aplicar balance F = S (sub-balance SAG)
    s = f
    
    # Calcular valores faltantes según los datos disponibles
    if p > 0 and r > 0:
        b = p + r
    elif b > 0 and p > 0:
        r = b - p
    elif b > 0 and r > 0:
        p = b - r
    else:
        # Valores típicos si no se especifican
        p = p or f * 0.8
        r = r or f * 0.2
        b = p + r
    
    # Validar que los valores sean positivos
    f = max(0, f)
    s = max(0, s)
    b = max(0, b)
    p = max(0, p)
    r = max(0, r)
    
    # Verificar balances
    balance_sag = abs(f - s) < 0.1  # F = S
    balance_bolas = abs((s + r) - b) < 0.1  # S + R = B
    balance_global = abs(f - (p + r)) < 0.1  # F = P + R
    
    return {
        'tipo_circuito': 'sabc1',
        'f_mineral': round(f, 2),
        's_producto_sag': round(s, 2),
        'b_producto_bolas': round(b, 2),
        'p_producto_final': round(p, 2),
        'r_carga_circulante': round(r, 2),
        'balance_verificado': balance_sag and balance_bolas and balance_global
    }

def calcular_circuito_sabc2(formulario):
    """Circuito SABC-2: Balance SAG F = S, Balance Bolas + Clasificador S + R = P + R => P = S"""
    # Obtener valores del formulario
    f = formulario.f_mineral_sabc2.data or 100.0
    s = formulario.s_producto_sag_sabc2.data or 0
    r = formulario.r_rechazo_sabc2.data or 0
    p = formulario.p_producto_final_sabc2.data or 0
    
    # Aplicar balances fundamentales
    s = f  # Balance SAG: F = S
    p = s  # Balance simplificado: P = S
    
    # Si no se especifica rechazo, usar valor típico
    if r == 0:
        r = f * 0.15  # 15% típico
    
    # Validar que los valores sean positivos
    f = max(0, f)
    s = max(0, s)
    r = max(0, r)
    p = max(0, p)
    
    # Calcular carga circulante CC = (R/P) * 100
    carga_circulante_pct = (r / p) * 100 if p > 0 else 0
    
    # Verificar balances
    balance_sag = abs(f - s) < 0.1  # F = S
    balance_producto = abs(p - s) < 0.1  # P = S
    
    return {
        'tipo_circuito': 'sabc2',
        'f_mineral': round(f, 2),
        's_producto_sag': round(s, 2),
        'r_rechazo': round(r, 2),
        'p_producto_final': round(p, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': balance_sag and balance_producto
    }

def crear_diagrama_flujo(resultados):
    """Crear gráfico de barras según tipo de circuito"""
    fig = go.Figure()
    tipo_circuito = resultados.get('tipo_circuito', 'directo')
    
    if tipo_circuito == 'directo':
        categorias = ['Alimentación (F)', 'Producto (P)', 'Rechazo (R)']
        valores = [resultados['f_alimentacion'], resultados['p_producto'], resultados['r_rechazo']]
        titulo = 'Circuito Cerrado Directo - Flujos'
        
    elif tipo_circuito == 'inverso':
        categorias = ['Alimentación (F)', 'Rechazo (R)', 'Producto (P)']
        valores = [resultados['f_alimentacion'], resultados['r_rechazo'], resultados['p_producto']]
        titulo = 'Circuito Cerrado Inverso - Flujos'
        
    elif tipo_circuito == 'sabc1':
        categorias = ['Mineral (F)', 'SAG (S)', 'Bolas (B)', 'Producto (P)', 'Circulante (R)']
        valores = [resultados['f_mineral'], resultados['s_producto_sag'], 
                  resultados['b_producto_bolas'], resultados['p_producto_final'], 
                  resultados['r_carga_circulante']]
        titulo = 'Circuito SABC-1 - Flujos'
        
    elif tipo_circuito == 'sabc2':
        categorias = ['Mineral (F)', 'SAG (S)', 'Rechazo (R)', 'Producto (P)']
        valores = [resultados['f_mineral'], resultados['s_producto_sag'], 
                  resultados['r_rechazo'], resultados['p_producto_final']]
        titulo = 'Circuito SABC-2 - Flujos'
    
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][:len(categorias)]
    
    fig.add_trace(go.Bar(
        x=categorias,
        y=valores,
        name='Flujos (t/h)',
        marker_color=colores,
        text=[f'{v:.1f} t/h' for v in valores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Flujos del Circuito',
        yaxis_title='Toneladas por Hora (t/h)',
        showlegend=False,
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_eficiencias(resultados):
    """Crear gráfico circular de carga circulante"""
    fig = go.Figure()
    
    if resultados.get('carga_circulante_pct'):
        carga_circulante = resultados['carga_circulante_pct']
        resto = 100 - min(carga_circulante, 100)
        
        fig.add_trace(go.Pie(
            labels=['Carga Circulante', 'Flujo Directo'],
            values=[carga_circulante, resto],
            hole=0.4,
            marker_colors=['#ff7f0e', '#2ca02c']
        ))
        
        fig.update_layout(
            title='Porcentaje de Carga Circulante',
            annotations=[dict(text=f'{carga_circulante:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
            height=400
        )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_distribucion(resultados):
    """Crear gráfico de verificación de balance"""
    fig = go.Figure()
    
    balance_verificado = resultados.get('balance_verificado', False)
    
    fig.add_trace(go.Bar(
        x=['Balance de Masa'],
        y=[100 if balance_verificado else 0],
        name='Verificación (%)',
        marker_color=['#2ca02c' if balance_verificado else '#d62728'],
        text=['Correcto' if balance_verificado else 'Error'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Verificación del Balance de Masa',
        xaxis_title='Estado del Balance',
        yaxis_title='Verificación (%)',
        showlegend=False,
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
