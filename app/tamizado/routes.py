
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.tamizado.forms import FormularioTamizado
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json

bp_tamizado = Blueprint('tamizado', __name__)

@bp_tamizado.route('/', methods=['GET', 'POST'])
@login_required
def analisis_granulometrico():
    formulario = FormularioTamizado()
    
    # Inicializar mallas estándar
    if not formulario.mallas.data or len(formulario.mallas.data) == 0:
        mallas_estandar = [25.4, 19.0, 12.7, 9.51, 6.35, 4.75, 2.38, 1.19]
        for abertura in mallas_estandar:
            formulario.mallas.append_entry({'abertura': abertura, 'peso_retenido': 0})
    
    grafico_json = None
    tabla_resultados = None
    
    if formulario.validate_on_submit():
        resultados = calcular_granulometria(formulario)
        tabla_resultados = resultados['tabla']
        grafico_json = resultados['grafico']
    
    return render_template('tamizado/analisis.html', 
                         formulario=formulario, 
                         grafico=grafico_json,
                         tabla=tabla_resultados)

def calcular_granulometria(formulario):
    peso_total = formulario.peso_total_muestra.data
    datos = []
    
    for malla in formulario.mallas.data:
        if malla['peso_retenido'] > 0:
            datos.append({
                'abertura': malla['abertura'],
                'peso_retenido': malla['peso_retenido']
            })
    
    df = pd.DataFrame(datos)
    df = df.sort_values('abertura', ascending=False)
    
    # Calcular porcentajes
    df['porcentaje_retenido'] = (df['peso_retenido'] / peso_total) * 100
    df['porcentaje_acumulado_retenido'] = df['porcentaje_retenido'].cumsum()
    df['porcentaje_pasante'] = 100 - df['porcentaje_acumulado_retenido']
    
    # Crear gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['abertura'],
        y=df['porcentaje_pasante'],
        mode='lines+markers',
        name='Curva Granulométrica',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Curva Granulométrica Acumulativa',
        xaxis_title='Abertura de Malla (mm)',
        yaxis_title='Porcentaje Pasante (%)',
        xaxis_type='log',
        template='plotly_white',
        height=500
    )
    
    grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return {
        'tabla': df.round(2).to_dict('records'),
        'grafico': grafico_json
    }
