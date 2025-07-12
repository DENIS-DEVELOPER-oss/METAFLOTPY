from flask import Blueprint, render_template
from app.balance_metalurgico.forms import FormularioBalanceMetalurgico
import plotly.graph_objs as go
import plotly.utils
import json

bp_balance_metalurgico = Blueprint('balance_metalurgico', __name__)

@bp_balance_metalurgico.route('/', methods=['GET', 'POST'])
def balance_metalurgico():
    formulario = FormularioBalanceMetalurgico()
    resultados = None
    graficos = {}

    if formulario.validate_on_submit():
        resultados = calcular_balance_metalurgico(formulario)
        graficos['recuperacion'] = crear_grafico_recuperacion(resultados)
        graficos['leyes'] = crear_grafico_leyes(resultados)
        graficos['balance_circular'] = crear_grafico_balance_circular(resultados)

    return render_template('balance_metalurgico/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         graficos=graficos)

def calcular_balance_metalurgico(formulario):
    # Cálculos de balance metalúrgico
    ley_alimentacion = formulario.ley_alimentacion.data
    ley_concentrado = formulario.ley_concentrado.data
    ley_relave = formulario.ley_relave.data
    razon_concentracion = formulario.razon_concentracion.data

    # Cálculo de recuperación metalúrgica
    recuperacion_metalurgica = ((ley_concentrado - ley_relave) / (ley_alimentacion - ley_relave)) * 100

    # Cálculo de recuperación en peso
    recuperacion_peso = (1 / razon_concentracion) * 100

    return {
        'ley_alimentacion': ley_alimentacion,
        'ley_concentrado': ley_concentrado,
        'ley_relave': ley_relave,
        'razon_concentracion': razon_concentracion,
        'recuperacion_metalurgica': recuperacion_metalurgica,
        'recuperacion_peso': recuperacion_peso
    }

def crear_grafico_recuperacion(resultados):
    # Crear gráfico de recuperaciones
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=['Recuperación Metalúrgica', 'Recuperación en Peso'],
        y=[resultados['recuperacion_metalurgica'], resultados['recuperacion_peso']],
        name='Recuperaciones (%)',
        marker_color=['#2ca02c', '#1f77b4'],
        text=[f"{resultados['recuperacion_metalurgica']:.2f}%", f"{resultados['recuperacion_peso']:.2f}%"],
        textposition='auto'
    ))

    fig.update_layout(
        title='Recuperaciones del Proceso',
        xaxis_title='Tipo de Recuperación',
        yaxis_title='Porcentaje (%)',
        showlegend=False,
        height=400
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_leyes(resultados):
    # Crear gráfico de leyes
    fig = go.Figure()
    
    leyes = [resultados['ley_alimentacion'], resultados['ley_concentrado'], resultados['ley_relave']]
    productos = ['Alimentación', 'Concentrado', 'Relave']
    colores = ['#ff7f0e', '#2ca02c', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=leyes,
        name='Leyes (%)',
        marker_color=colores,
        text=[f'{ley:.2f}%' for ley in leyes],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Distribución de Leyes por Producto',
        xaxis_title='Productos',
        yaxis_title='Ley (%)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_balance_circular(resultados):
    # Crear gráfico circular del balance
    fig = go.Figure()
    
    recuperacion_met = resultados['recuperacion_metalurgica']
    perdida_met = 100 - recuperacion_met
    
    fig.add_trace(go.Pie(
        labels=['Metal Recuperado', 'Metal Perdido'],
        values=[recuperacion_met, perdida_met],
        hole=0.4,
        marker_colors=['#2ca02c', '#d62728']
    ))
    
    fig.update_layout(
        title='Balance Metalúrgico',
        annotations=[dict(text=f'{recuperacion_met:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)