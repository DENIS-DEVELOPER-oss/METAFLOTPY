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
    grafico_json = None

    if formulario.validate_on_submit():
        resultados = calcular_balance_metalurgico(formulario)
        grafico_json = crear_grafico_recuperacion(resultados)

    return render_template('balance_metalurgico/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         grafico=grafico_json)

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
        marker_color=['blue', 'green']
    ))

    fig.update_layout(
        title='Recuperaciones del Proceso',
        xaxis_title='Tipo de Recuperación',
        yaxis_title='Porcentaje (%)',
        showlegend=False
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)