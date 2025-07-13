
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
    error_mensaje = None

    if formulario.validate_on_submit():
        print(f"Formulario validado. Tipo balance: {formulario.tipo_balance.data}")
        try:
            resultados = calcular_balance_metalurgico(formulario)
            if resultados:
                print("Resultados calculados exitosamente")
                # Crear gráficos según el tipo de balance
                if formulario.tipo_balance.data == '1_concentrado':
                    graficos['recuperacion'] = crear_grafico_recuperacion_1(resultados)
                    graficos['leyes'] = crear_grafico_leyes_1(resultados)
                    graficos['diagrama_flujo'] = crear_diagrama_flujo_1(resultados)
                elif formulario.tipo_balance.data == '2_concentrados':
                    graficos['recuperaciones'] = crear_grafico_recuperaciones_2(resultados)
                    graficos['leyes'] = crear_grafico_leyes_2(resultados)
                    graficos['diagrama_flujo'] = crear_diagrama_flujo_2(resultados)
                elif formulario.tipo_balance.data == '3_concentrados':
                    graficos['recuperaciones'] = crear_grafico_recuperaciones_3(resultados)
                    graficos['leyes'] = crear_grafico_leyes_3(resultados)
                    graficos['diagrama_flujo'] = crear_diagrama_flujo_3(resultados)
            else:
                error_mensaje = "Error en el cálculo. Verifique que ha ingresado suficientes datos válidos."
        except Exception as e:
            print(f"Error en cálculo: {e}")
            error_mensaje = f"Error en el cálculo: {str(e)}"
    elif formulario.errors:
        print(f"Errores de validación: {formulario.errors}")
        error_mensaje = "Error en los datos ingresados. Verifique los valores."

    return render_template('balance_metalurgico/balance.html', 
                         formulario=formulario, 
                         resultados=resultados,
                         graficos=graficos,
                         error_mensaje=error_mensaje)

def calcular_balance_metalurgico(formulario):
    tipo_balance = formulario.tipo_balance.data
    
    if tipo_balance == '1_concentrado':
        return calcular_balance_1_concentrado(formulario)
    elif tipo_balance == '2_concentrados':
        return calcular_balance_2_concentrados(formulario)
    elif tipo_balance == '3_concentrados':
        return calcular_balance_3_concentrados(formulario)
    
    return None

def calcular_balance_1_concentrado(formulario):
    """Balance Metalúrgico - 1 Concentrado"""
    # Obtener valores del formulario
    F = formulario.f_masa_alimentacion.data or 0
    C = formulario.c_masa_concentrado.data or 0
    T = formulario.t_masa_relave.data or 0
    f = formulario.f_ley_alimentacion.data or 0
    c = formulario.c_ley_concentrado.data or 0
    t = formulario.t_ley_relave.data or 0
    
    # Contar valores válidos
    valores_masa = [v for v in [F, C, T] if v > 0]
    valores_ley = [v for v in [f, c, t] if v > 0]
    
    if len(valores_masa) < 2 or len(valores_ley) < 2:
        raise ValueError("Se requieren al menos 2 valores de masa y 2 valores de ley")
    
    # Balance de masa global: F = C + T
    if F > 0 and C > 0 and T == 0:
        T = F - C
    elif F > 0 and T > 0 and C == 0:
        C = F - T
    elif C > 0 and T > 0 and F == 0:
        F = C + T
    
    # Balance de metal: F * f = C * c + T * t
    if F > 0 and f > 0 and C > 0 and c > 0 and t == 0:
        if T > 0:
            t = (F * f - C * c) / T
    elif F > 0 and f > 0 and T > 0 and t > 0 and c == 0:
        if C > 0:
            c = (F * f - T * t) / C
    elif C > 0 and c > 0 and T > 0 and t > 0 and f == 0:
        if F > 0:
            f = (C * c + T * t) / F
    
    # Calcular recuperación metalúrgica: R = (C * c) / (F * f) * 100
    if F > 0 and f > 0 and C > 0 and c > 0:
        recuperacion = (C * c) / (F * f) * 100
    else:
        recuperacion = 0
    
    # Verificar balances
    balance_masa_ok = abs(F - (C + T)) < 0.01 if F > 0 and C > 0 and T > 0 else False
    balance_metal_ok = abs(F * f - (C * c + T * t)) < 0.01 if all(v > 0 for v in [F, f, C, c, T, t]) else False
    
    return {
        'tipo_balance': '1_concentrado',
        'F': round(F, 2) if F > 0 else 0,
        'C': round(C, 2) if C > 0 else 0,
        'T': round(T, 2) if T > 0 else 0,
        'f': round(f, 3) if f > 0 else 0,
        'c': round(c, 3) if c > 0 else 0,
        't': round(t, 3) if t > 0 else 0,
        'recuperacion': round(recuperacion, 2),
        'balance_masa_ok': balance_masa_ok,
        'balance_metal_ok': balance_metal_ok,
        'metal_alimentacion': round(F * f, 2) if F > 0 and f > 0 else 0,
        'metal_concentrado': round(C * c, 2) if C > 0 and c > 0 else 0,
        'metal_relave': round(T * t, 2) if T > 0 and t > 0 else 0
    }

def calcular_balance_2_concentrados(formulario):
    """Balance Metalúrgico - 2 Concentrados"""
    # Obtener valores del formulario
    F = formulario.f_masa_alimentacion.data or 0
    C1 = formulario.c1_masa_concentrado1.data or 0
    C2 = formulario.c2_masa_concentrado2.data or 0
    T = formulario.t_masa_relave.data or 0
    f = formulario.f_ley_alimentacion.data or 0
    c1 = formulario.c1_ley_concentrado1.data or 0
    c2 = formulario.c2_ley_concentrado2.data or 0
    t = formulario.t_ley_relave.data or 0
    
    # Masa total: F = C1 + C2 + T
    valores_masa = [v for v in [F, C1, C2, T] if v > 0]
    if len(valores_masa) < 3:
        # Calcular valores faltantes usando valores por defecto
        if F == 0 and len(valores_masa) >= 3:
            F = C1 + C2 + T
        elif C1 == 0 and F > 0 and C2 > 0 and T > 0:
            C1 = F - C2 - T
        elif C2 == 0 and F > 0 and C1 > 0 and T > 0:
            C2 = F - C1 - T
        elif T == 0 and F > 0 and C1 > 0 and C2 > 0:
            T = F - C1 - C2
    
    # Balance metálico: F * f = C1 * c1 + C2 * c2 + T * t
    # Recuperaciones parciales
    R1 = (C1 * c1) / (F * f) * 100 if F > 0 and f > 0 and C1 > 0 and c1 > 0 else 0
    R2 = (C2 * c2) / (F * f) * 100 if F > 0 and f > 0 and C2 > 0 and c2 > 0 else 0
    
    # Recuperación total
    R_total = R1 + R2
    
    # Verificar balances
    balance_masa_ok = abs(F - (C1 + C2 + T)) < 0.01 if all(v > 0 for v in [F, C1, C2, T]) else False
    balance_metal_ok = abs(F * f - (C1 * c1 + C2 * c2 + T * t)) < 0.01 if all(v > 0 for v in [F, f, C1, c1, C2, c2, T, t]) else False
    
    return {
        'tipo_balance': '2_concentrados',
        'F': round(F, 2) if F > 0 else 0,
        'C1': round(C1, 2) if C1 > 0 else 0,
        'C2': round(C2, 2) if C2 > 0 else 0,
        'T': round(T, 2) if T > 0 else 0,
        'f': round(f, 3) if f > 0 else 0,
        'c1': round(c1, 3) if c1 > 0 else 0,
        'c2': round(c2, 3) if c2 > 0 else 0,
        't': round(t, 3) if t > 0 else 0,
        'R1': round(R1, 2),
        'R2': round(R2, 2),
        'R_total': round(R_total, 2),
        'balance_masa_ok': balance_masa_ok,
        'balance_metal_ok': balance_metal_ok,
        'metal_alimentacion': round(F * f, 2) if F > 0 and f > 0 else 0,
        'metal_concentrado1': round(C1 * c1, 2) if C1 > 0 and c1 > 0 else 0,
        'metal_concentrado2': round(C2 * c2, 2) if C2 > 0 and c2 > 0 else 0,
        'metal_relave': round(T * t, 2) if T > 0 and t > 0 else 0
    }

def calcular_balance_3_concentrados(formulario):
    """Balance Metalúrgico - 3 Concentrados"""
    # Obtener valores del formulario
    F = formulario.f_masa_alimentacion.data or 0
    C1 = formulario.c1_masa_concentrado1.data or 0
    C2 = formulario.c2_masa_concentrado2.data or 0
    C3 = formulario.c3_masa_concentrado3.data or 0
    T = formulario.t_masa_relave.data or 0
    f = formulario.f_ley_alimentacion.data or 0
    c1 = formulario.c1_ley_concentrado1.data or 0
    c2 = formulario.c2_ley_concentrado2.data or 0
    c3 = formulario.c3_ley_concentrado3.data or 0
    t = formulario.t_ley_relave.data or 0
    
    # Balance de masa: F = C1 + C2 + C3 + T
    valores_masa = [v for v in [F, C1, C2, C3, T] if v > 0]
    if len(valores_masa) < 4:
        # Calcular valores faltantes
        if F == 0 and len(valores_masa) >= 4:
            F = C1 + C2 + C3 + T
        elif T == 0 and F > 0 and C1 > 0 and C2 > 0 and C3 > 0:
            T = F - C1 - C2 - C3
    
    # Balance metálico: F * f = C1 * c1 + C2 * c2 + C3 * c3 + T * t
    # Recuperaciones por concentrado: Ri = (Ci * ci) / (F * f) * 100
    R1 = (C1 * c1) / (F * f) * 100 if F > 0 and f > 0 and C1 > 0 and c1 > 0 else 0
    R2 = (C2 * c2) / (F * f) * 100 if F > 0 and f > 0 and C2 > 0 and c2 > 0 else 0
    R3 = (C3 * c3) / (F * f) * 100 if F > 0 and f > 0 and C3 > 0 and c3 > 0 else 0
    
    # Recuperación total: Rtotal = R1 + R2 + R3
    R_total = R1 + R2 + R3
    
    # Verificar balances
    balance_masa_ok = abs(F - (C1 + C2 + C3 + T)) < 0.01 if all(v > 0 for v in [F, C1, C2, C3, T]) else False
    balance_metal_ok = abs(F * f - (C1 * c1 + C2 * c2 + C3 * c3 + T * t)) < 0.01 if all(v > 0 for v in [F, f, C1, c1, C2, c2, C3, c3, T, t]) else False
    
    return {
        'tipo_balance': '3_concentrados',
        'F': round(F, 2) if F > 0 else 0,
        'C1': round(C1, 2) if C1 > 0 else 0,
        'C2': round(C2, 2) if C2 > 0 else 0,
        'C3': round(C3, 2) if C3 > 0 else 0,
        'T': round(T, 2) if T > 0 else 0,
        'f': round(f, 3) if f > 0 else 0,
        'c1': round(c1, 3) if c1 > 0 else 0,
        'c2': round(c2, 3) if c2 > 0 else 0,
        'c3': round(c3, 3) if c3 > 0 else 0,
        't': round(t, 3) if t > 0 else 0,
        'R1': round(R1, 2),
        'R2': round(R2, 2),
        'R3': round(R3, 2),
        'R_total': round(R_total, 2),
        'balance_masa_ok': balance_masa_ok,
        'balance_metal_ok': balance_metal_ok,
        'metal_alimentacion': round(F * f, 2) if F > 0 and f > 0 else 0,
        'metal_concentrado1': round(C1 * c1, 2) if C1 > 0 and c1 > 0 else 0,
        'metal_concentrado2': round(C2 * c2, 2) if C2 > 0 and c2 > 0 else 0,
        'metal_concentrado3': round(C3 * c3, 2) if C3 > 0 and c3 > 0 else 0,
        'metal_relave': round(T * t, 2) if T > 0 and t > 0 else 0
    }

# Funciones para crear gráficos - Balance 1 Concentrado
def crear_grafico_recuperacion_1(resultados):
    fig = go.Figure()
    
    recuperacion = resultados['recuperacion']
    perdida = 100 - recuperacion
    
    fig.add_trace(go.Pie(
        labels=['Metal Recuperado', 'Metal Perdido'],
        values=[recuperacion, perdida],
        hole=0.4,
        marker_colors=['#2ca02c', '#d62728']
    ))
    
    fig.update_layout(
        title='Recuperación Metalúrgica',
        annotations=[dict(text=f'{recuperacion:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_leyes_1(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado', 'Relave']
    leyes = [resultados['f'], resultados['c'], resultados['t']]
    colores = ['#ff7f0e', '#2ca02c', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=leyes,
        name='Leyes',
        marker_color=colores,
        text=[f'{ley:.3f}' for ley in leyes],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Distribución de Leyes por Producto',
        xaxis_title='Productos',
        yaxis_title='Ley (% o g/t)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_diagrama_flujo_1(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado', 'Relave']
    masas = [resultados['F'], resultados['C'], resultados['T']]
    colores = ['#1f77b4', '#2ca02c', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=masas,
        name='Flujos de Masa',
        marker_color=colores,
        text=[f'{masa:.1f} t' for masa in masas],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Diagrama de Flujos - Balance 1 Concentrado',
        xaxis_title='Corrientes',
        yaxis_title='Masa (t/día o t/h)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Funciones para crear gráficos - Balance 2 Concentrados
def crear_grafico_recuperaciones_2(resultados):
    fig = go.Figure()
    
    recuperaciones = ['R₁', 'R₂', 'R Total']
    valores = [resultados['R1'], resultados['R2'], resultados['R_total']]
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    fig.add_trace(go.Bar(
        x=recuperaciones,
        y=valores,
        name='Recuperaciones',
        marker_color=colores,
        text=[f'{val:.2f}%' for val in valores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Recuperaciones Parciales y Total',
        xaxis_title='Tipo de Recuperación',
        yaxis_title='Recuperación (%)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_leyes_2(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado 1', 'Concentrado 2', 'Relave']
    leyes = [resultados['f'], resultados['c1'], resultados['c2'], resultados['t']]
    colores = ['#ff7f0e', '#2ca02c', '#1f77b4', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=leyes,
        name='Leyes',
        marker_color=colores,
        text=[f'{ley:.3f}' for ley in leyes],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Distribución de Leyes - 2 Concentrados',
        xaxis_title='Productos',
        yaxis_title='Ley (% o g/t)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_diagrama_flujo_2(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado 1', 'Concentrado 2', 'Relave']
    masas = [resultados['F'], resultados['C1'], resultados['C2'], resultados['T']]
    colores = ['#ff7f0e', '#2ca02c', '#1f77b4', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=masas,
        name='Flujos de Masa',
        marker_color=colores,
        text=[f'{masa:.1f} t' for masa in masas],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Diagrama de Flujos - Balance 2 Concentrados',
        xaxis_title='Corrientes',
        yaxis_title='Masa (t/día o t/h)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# Funciones para crear gráficos - Balance 3 Concentrados
def crear_grafico_recuperaciones_3(resultados):
    fig = go.Figure()
    
    recuperaciones = ['R₁', 'R₂', 'R₃', 'R Total']
    valores = [resultados['R1'], resultados['R2'], resultados['R3'], resultados['R_total']]
    colores = ['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c']
    
    fig.add_trace(go.Bar(
        x=recuperaciones,
        y=valores,
        name='Recuperaciones',
        marker_color=colores,
        text=[f'{val:.2f}%' for val in valores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Recuperaciones por Concentrado y Total',
        xaxis_title='Tipo de Recuperación',
        yaxis_title='Recuperación (%)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_grafico_leyes_3(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado 1', 'Concentrado 2', 'Concentrado 3', 'Relave']
    leyes = [resultados['f'], resultados['c1'], resultados['c2'], resultados['c3'], resultados['t']]
    colores = ['#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=leyes,
        name='Leyes',
        marker_color=colores,
        text=[f'{ley:.3f}' for ley in leyes],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Distribución de Leyes - 3 Concentrados',
        xaxis_title='Productos',
        yaxis_title='Ley (% o g/t)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def crear_diagrama_flujo_3(resultados):
    fig = go.Figure()
    
    productos = ['Alimentación', 'Concentrado 1', 'Concentrado 2', 'Concentrado 3', 'Relave']
    masas = [resultados['F'], resultados['C1'], resultados['C2'], resultados['C3'], resultados['T']]
    colores = ['#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd', '#d62728']
    
    fig.add_trace(go.Bar(
        x=productos,
        y=masas,
        name='Flujos de Masa',
        marker_color=colores,
        text=[f'{masa:.1f} t' for masa in masas],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Diagrama de Flujos - Balance 3 Concentrados',
        xaxis_title='Corrientes',
        yaxis_title='Masa (t/día o t/h)',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
