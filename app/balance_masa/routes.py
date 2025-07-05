
from flask import Blueprint, render_template
from flask_login import login_required
from app.balance_masa.forms import FormularioBalanceMasa
import plotly.graph_objs as go
import plotly.utils
import json

bp_balance_masa = Blueprint('balance_masa', __name__)

@bp_balance_masa.route('/', methods=['GET', 'POST'])
@login_required
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
    F = formulario.alimentacion_fresca.data  # t/h
    CCR = formulario.razon_carga_circulante.data
    E = formulario.eficiencia_clasificador.data / 100
    
    # Cálculos del balance de masa
    L = F * CCR  # Carga circulante
    A = F + L    # Alimentación total al molino
    U = A * (1 - E)  # Descarga del clasificador
    O = A * E    # Rebose del clasificador
    
    return {
        'alimentacion_fresca': F,
        'carga_circulante': round(L, 2),
        'alimentacion_molino': round(A, 2),
        'descarga_clasificador': round(U, 2),
        'rebose_clasificador': round(O, 2),
        'razon_carga_circulante': CCR,
        'eficiencia_clasificador': formulario.eficiencia_clasificador.data
    }

def crear_diagrama_flujo(resultados):
    # Crear diagrama de flujo simplificado
    fig = go.Figure()
    
    # Datos para el gráfico de barras
    flujos = ['Alimentación\nFresca', 'Carga\nCirculante', 'Alimentación\nMolino', 
              'Descarga\nClasificador', 'Rebose\nClasificador']
    valores = [resultados['alimentacion_fresca'], resultados['carga_circulante'],
               resultados['alimentacion_molino'], resultados['descarga_clasificador'],
               resultados['rebose_clasificador']]
    
    fig.add_trace(go.Bar(
        x=flujos,
        y=valores,
        marker_color=['#ff7f0e', '#2ca02c', '#1f77b4', '#d62728', '#9467bd'],
        text=[f'{v:.1f} t/h' for v in valores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Diagrama de Flujos - Balance de Masa',
        yaxis_title='Flujo Másico (t/h)',
        template='plotly_white',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
