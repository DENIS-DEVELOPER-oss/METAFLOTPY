
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Optional

class FormularioTamizado(FlaskForm):
    peso_total = FloatField('Peso Total de Muestra (g)', 
                           validators=[DataRequired(), NumberRange(min=0.1)])
    
    # Mallas estándar ASTM
    retenido_12_5 = FloatField('Retenido 12.5 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_9_5 = FloatField('Retenido 9.5 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_6_35 = FloatField('Retenido 6.35 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_4_75 = FloatField('Retenido 4.75 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_3_35 = FloatField('Retenido 3.35 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_2_36 = FloatField('Retenido 2.36 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_1_18 = FloatField('Retenido 1.18 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_85 = FloatField('Retenido 0.85 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_60 = FloatField('Retenido 0.60 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_425 = FloatField('Retenido 0.425 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_30 = FloatField('Retenido 0.30 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_212 = FloatField('Retenido 0.212 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_150 = FloatField('Retenido 0.150 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_106 = FloatField('Retenido 0.106 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_0_075 = FloatField('Retenido 0.075 mm', validators=[Optional(), NumberRange(min=0)])
    retenido_fondo = FloatField('Retenido Fondo', validators=[Optional(), NumberRange(min=0)])
    
    calcular = SubmitField('Calcular Análisis Granulométrico')

class FormularioRegresionLineal(FlaskForm):
    # Campos para porcentajes pasantes
    pasante_12_5 = FloatField('Pasante 12.5 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_9_5 = FloatField('Pasante 9.5 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_6_35 = FloatField('Pasante 6.35 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_4_75 = FloatField('Pasante 4.75 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_3_35 = FloatField('Pasante 3.35 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_2_36 = FloatField('Pasante 2.36 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_1_18 = FloatField('Pasante 1.18 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_85 = FloatField('Pasante 0.85 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_60 = FloatField('Pasante 0.60 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_425 = FloatField('Pasante 0.425 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_30 = FloatField('Pasante 0.30 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_212 = FloatField('Pasante 0.212 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_150 = FloatField('Pasante 0.150 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_106 = FloatField('Pasante 0.106 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_075 = FloatField('Pasante 0.075 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_fondo = FloatField('Pasante Fondo (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    
    calcular = SubmitField('Calcular Regresión Lineal')

class FormularioRosinRammler(FlaskForm):
    # Campos para porcentajes pasantes
    pasante_12_5 = FloatField('Pasante 12.5 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_9_5 = FloatField('Pasante 9.5 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_6_35 = FloatField('Pasante 6.35 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_4_75 = FloatField('Pasante 4.75 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_3_35 = FloatField('Pasante 3.35 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_2_36 = FloatField('Pasante 2.36 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_1_18 = FloatField('Pasante 1.18 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_85 = FloatField('Pasante 0.85 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_60 = FloatField('Pasante 0.60 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_425 = FloatField('Pasante 0.425 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_30 = FloatField('Pasante 0.30 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_212 = FloatField('Pasante 0.212 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_150 = FloatField('Pasante 0.150 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_106 = FloatField('Pasante 0.106 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_0_075 = FloatField('Pasante 0.075 mm (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    pasante_fondo = FloatField('Pasante Fondo (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    
    calcular = SubmitField('Calcular Rosin-Rammler')
