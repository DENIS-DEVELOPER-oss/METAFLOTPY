
from flask import Blueprint, render_template, request, jsonify
from app.tamizado.forms import FormularioTamizado
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json

bp_tamizado = Blueprint('tamizado', __name__)

@bp_tamizado.route('/', methods=['GET', 'POST'])
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
    # Función de cálculo granulométrico (simplificada)
    mallas = []
    pesos = []
    
    for malla in formulario.mallas.data:
        mallas.append(malla['abertura'])
        pesos.append(malla['peso_retenido'])
    
    # Crear DataFrame
    df = pd.DataFrame({
        'Abertura_mm': mallas,
        'Peso_Retenido_g': pesos
    })
    
    # Calcular porcentajes
    peso_total = df['Peso_Retenido_g'].sum()
    df['Porcentaje_Retenido'] = (df['Peso_Retenido_g'] / peso_total) * 100
    df['Porcentaje_Acumulado'] = df['Porcentaje_Retenido'].cumsum()
    df['Porcentaje_Pasante'] = 100 - df['Porcentaje_Acumulado']
    
    # Crear gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Abertura_mm'],
        y=df['Porcentaje_Pasante'],
        mode='lines+markers',
        name='Curva Granulométrica',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title='Curva Granulométrica',
        xaxis_title='Abertura de Malla (mm)',
        yaxis_title='Porcentaje Pasante (%)',
        xaxis_type='log',
        grid=True
    )
    
    grafico_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return {
        'tabla': df.to_dict('records'),
        'grafico': grafico_json
    }
