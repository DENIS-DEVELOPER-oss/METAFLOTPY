
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
    # Obtener datos del formulario
    tipo_circuito = formulario.tipo_circuito.data
    alimentacion_fresca = formulario.alimentacion_fresca.data
    razon_carga_circulante = formulario.razon_carga_circulante.data
    eficiencia = formulario.eficiencia_clasificador.data / 100
    
    # Cálculos básicos según tipo de circuito
    carga_circulante = razon_carga_circulante * alimentacion_fresca
    
    if tipo_circuito == 'directo':
        # Circuito cerrado directo
        alimentacion_molino = alimentacion_fresca + carga_circulante
        descarga_clasificador = carga_circulante
        rebose_clasificador = alimentacion_fresca
        
    elif tipo_circuito == 'inverso':
        # Circuito cerrado inverso
        alimentacion_molino = alimentacion_fresca + carga_circulante
        descarga_clasificador = carga_circulante
        rebose_clasificador = alimentacion_fresca
        
    elif tipo_circuito == 'sabc1':
        # Circuito SABC-1
        alimentacion_molino = alimentacion_fresca + (carga_circulante * 0.8)
        descarga_clasificador = carga_circulante
        rebose_clasificador = alimentacion_fresca
        
    elif tipo_circuito == 'sabc2':
        # Circuito SABC-2
        alimentacion_molino = alimentacion_fresca + (carga_circulante * 0.6)
        descarga_clasificador = carga_circulante
        rebose_clasificador = alimentacion_fresca
        
    else:
        # Valores por defecto
        alimentacion_molino = alimentacion_fresca + carga_circulante
        descarga_clasificador = carga_circulante
        rebose_clasificador = alimentacion_fresca
    
    return {
        'tipo_circuito': tipo_circuito,
        'alimentacion_fresca': round(alimentacion_fresca, 2),
        'carga_circulante': round(carga_circulante, 2),
        'alimentacion_molino': round(alimentacion_molino, 2),
        'descarga_clasificador': round(descarga_clasificador, 2),
        'rebose_clasificador': round(rebose_clasificador, 2),
        'eficiencia_clasificador': round(eficiencia * 100, 1)
    }

def crear_diagrama_flujo(resultados):
    # Crear gráfico de barras según tipo de circuito
    fig = go.Figure()
    
    tipo_circuito = resultados.get('tipo_circuito', 'directo')
    
    # Títulos según tipo de circuito
    titulos_circuito = {
        'directo': 'Circuito Cerrado Directo',
        'inverso': 'Circuito Cerrado Inverso',
        'sabc1': 'Circuito SABC-1',
        'sabc2': 'Circuito SABC-2'
    }
    
    categorias = ['Alimentación Fresca', 'Carga Circulante', 'Alimentación al Molino', 'Descarga', 'Rebose']
    valores = [
        resultados['alimentacion_fresca'],
        resultados['carga_circulante'],
        resultados['alimentacion_molino'],
        resultados['descarga_clasificador'],
        resultados['rebose_clasificador']
    ]
    
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    fig.add_trace(go.Bar(
        x=categorias,
        y=valores,
        name='Flujos (t/h)',
        marker_color=colores,
        text=[f'{v:.1f} t/h' for v in valores],
        textposition='auto'
    ))
    
    titulo = f'Diagrama de Flujos - {titulos_circuito.get(tipo_circuito, "Balance de Masa")}'
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Flujos del Circuito',
        yaxis_title='Toneladas por Hora (t/h)',
        showlegend=False,
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
