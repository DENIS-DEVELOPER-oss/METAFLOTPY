
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
    grafico_json = None
    
    if formulario.validate_on_submit():
        resultados = calcular_balance_masa(formulario)
        grafico_json = crear_diagrama_flujo(resultados)
    
    return render_template('balance_masa/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

def calcular_balance_masa(formulario):
    # Cálculos simplificados de balance de masa
    alimentacion_fresca = formulario.alimentacion_fresca.data
    carga_circulante = formulario.carga_circulante.data
    eficiencia = formulario.eficiencia.data / 100
    
    # Cálculos básicos
    carga_total = alimentacion_fresca * (1 + carga_circulante)
    overflow = carga_total * eficiencia
    underflow = carga_total - overflow
    
    return {
        'alimentacion_fresca': alimentacion_fresca,
        'carga_circulante': carga_circulante * alimentacion_fresca,
        'carga_total': carga_total,
        'overflow': overflow,
        'underflow': underflow,
        'eficiencia': eficiencia * 100
    }

def crear_diagrama_flujo(resultados):
    # Crear gráfico de barras simple
    fig = go.Figure()
    
    categorias = ['Alimentación Fresca', 'Carga Circulante', 'Overflow', 'Underflow']
    valores = [
        resultados['alimentacion_fresca'],
        resultados['carga_circulante'],
        resultados['overflow'],
        resultados['underflow']
    ]
    
    fig.add_trace(go.Bar(
        x=categorias,
        y=valores,
        name='Flujos (t/h)',
        marker_color=['blue', 'green', 'orange', 'red']
    ))
    
    fig.update_layout(
        title='Diagrama de Flujos - Balance de Masa',
        xaxis_title='Flujos',
        yaxis_title='Toneladas por Hora (t/h)',
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
