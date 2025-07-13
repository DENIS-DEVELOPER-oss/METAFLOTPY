
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
    # Validar que se tengan al menos 2 valores para calcular el tercero
    f = formulario.f_alimentacion.data
    p = formulario.p_producto.data  
    r = formulario.r_rechazo.data
    
    # Calcular el valor faltante usando F = P + R
    if f and p and not r:
        r = f - p
    elif f and r and not p:
        p = f - r
    elif p and r and not f:
        f = p + r
    elif not (f and p and r):
        # Si no hay suficientes datos, usar valores por defecto
        if not f: f = 100
        if not p: p = 80
        if not r: r = f - p
    
    # Calcular carga circulante CC = (R/P) * 100
    carga_circulante_pct = (r / p) * 100 if p > 0 else 0
    
    return {
        'tipo_circuito': 'directo',
        'f_alimentacion': round(f, 2),
        'p_producto': round(p, 2),
        'r_rechazo': round(r, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': abs((f) - (p + r)) < 0.1
    }

def calcular_circuito_inverso(formulario):
    """Circuito Cerrado Inverso: F + R = P"""
    f = formulario.f_alimentacion_inv.data
    r = formulario.r_rechazo_inv.data
    p = formulario.p_producto_inv.data
    
    # Calcular el valor faltante usando F + R = P
    if f and r and not p:
        p = f + r
    elif f and p and not r:
        r = p - f
    elif r and p and not f:
        f = p - r
    elif not (f and r and p):
        # Valores por defecto
        if not f: f = 100
        if not r: r = 20
        if not p: p = f + r
    
    # Calcular carga circulante CC = (R/F) * 100
    carga_circulante_pct = (r / f) * 100 if f > 0 else 0
    
    return {
        'tipo_circuito': 'inverso',
        'f_alimentacion': round(f, 2),
        'r_rechazo': round(r, 2),
        'p_producto': round(p, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': abs((f + r) - p) < 0.1
    }

def calcular_circuito_sabc1(formulario):
    """Circuito SABC-1: Balance global F = P + R, Sub-balance SAG F = S, Sub-balance molino bolas S + R = B y B = P + R"""
    f = formulario.f_mineral_sabc1.data or 100
    s = formulario.s_producto_sag.data or f  # F = S
    b = formulario.b_producto_bolas.data
    p = formulario.p_producto_final_sabc1.data
    r = formulario.r_carga_circulante_sabc1.data
    
    # Aplicar balance F = S (sub-balance SAG)
    s = f
    
    # Si tenemos P y R, calcular B = P + R
    if p and r:
        b = p + r
    # Si tenemos B y P, calcular R = B - P
    elif b and p:
        r = b - p
    # Si tenemos B y R, calcular P = B - R
    elif b and r:
        p = b - r
    else:
        # Valores por defecto
        if not p: p = f * 0.8
        if not r: r = f * 0.2
        if not b: b = p + r
    
    # Verificar S + R = B
    s_r_balance = abs((s + r) - b) < 0.1
    
    return {
        'tipo_circuito': 'sabc1',
        'f_mineral': round(f, 2),
        's_producto_sag': round(s, 2),
        'b_producto_bolas': round(b, 2),
        'p_producto_final': round(p, 2),
        'r_carga_circulante': round(r, 2),
        'balance_verificado': s_r_balance and abs((f) - (p + r)) < 0.1
    }

def calcular_circuito_sabc2(formulario):
    """Circuito SABC-2: Balance SAG F = S, Balance Bolas + Clasificador S + R = P + R => P = S"""
    f = formulario.f_mineral_sabc2.data or 100
    s = formulario.s_producto_sag_sabc2.data or f  # F = S
    r = formulario.r_rechazo_sabc2.data
    p = formulario.p_producto_final_sabc2.data or s  # P = S
    
    # Aplicar balances
    s = f  # Balance SAG: F = S
    p = s  # Balance simplificado: P = S
    
    if not r:
        r = f * 0.15  # Valor típico
    
    # Calcular carga circulante CC = (R/P) * 100
    carga_circulante_pct = (r / p) * 100 if p > 0 else 0
    
    return {
        'tipo_circuito': 'sabc2',
        'f_mineral': round(f, 2),
        's_producto_sag': round(s, 2),
        'r_rechazo': round(r, 2),
        'p_producto_final': round(p, 2),
        'carga_circulante_pct': round(carga_circulante_pct, 1),
        'balance_verificado': abs(f - s) < 0.1 and abs(p - s) < 0.1
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
