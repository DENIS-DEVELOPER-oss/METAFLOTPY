
from flask import Blueprint, render_template
from flask_login import login_required
from app.balance_metalurgico.forms import FormularioBalanceMetalurgico
import plotly.graph_objs as go
import plotly.utils
import json

bp_balance_metalurgico = Blueprint('balance_metalurgico', __name__)

@bp_balance_metalurgico.route('/', methods=['GET', 'POST'])
@login_required
def balance_metalurgico():
    formulario = FormularioBalanceMetalurgico()
    resultados = None
    grafico_json = None
    
    if formulario.validate_on_submit():
        resultados = calcular_balance_metalurgico(formulario)
        grafico_json = crear_grafico_recuperacion(resultados)
    
    return render_template('balance_metalurgico/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

def calcular_balance_metalurgico(formulario):
    f = formulario.ley_alimentacion.data / 100
    c = formulario.ley_concentrado.data / 100
    t = formulario.ley_relave.data / 100
    K = formulario.razon_concentracion.data
    
    # Recuperación metalúrgica
    R = ((f - t) / (c - t)) * 100
    
    # Ratio de concentración teórico
    K_teorico = (c - t) / (f - t)
    
    # Distribución de masa
    gamma = 1 / K  # Recuperación en peso
    
    return {
        'recuperacion_metalurgica': round(R, 2),
        'razon_concentracion_teorica': round(K_teorico, 2),
        'razon_concentracion_actual': K,
        'recuperacion_peso': round(gamma * 100, 2),
        'ley_alimentacion': formulario.ley_alimentacion.data,
        'ley_concentrado': formulario.ley_concentrado.data,
        'ley_relave': formulario.ley_relave.data
    }

def crear_grafico_recuperacion(resultados):
    # Gráfico de barras para mostrar leyes y recuperaciones
    fig = go.Figure()
    
    # Leyes
    fig.add_trace(go.Bar(
        name='Leyes (%)',
        x=['Alimentación', 'Concentrado', 'Relave'],
        y=[resultados['ley_alimentacion'], resultados['ley_concentrado'], resultados['ley_relave']],
        marker_color='lightblue',
        yaxis='y'
    ))
    
    # Crear segundo eje Y para recuperaciones
    fig.add_trace(go.Scatter(
        name='Recuperación Metalúrgica (%)',
        x=['Concentrado'],
        y=[resultados['recuperacion_metalurgica']],
        mode='markers',
        marker=dict(size=15, color='red'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Balance Metalúrgico - Leyes y Recuperación',
        xaxis_title='Productos',
        yaxis=dict(title='Ley (%)', side='left'),
        yaxis2=dict(title='Recuperación (%)', side='right', overlaying='y'),
        template='plotly_white',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
