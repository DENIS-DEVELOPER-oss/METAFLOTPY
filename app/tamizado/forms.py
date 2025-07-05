
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

class DatosMalla(FlaskForm):
    abertura = FloatField('Abertura (mm)', validators=[DataRequired(), NumberRange(min=0.001)])
    peso_retenido = FloatField('Peso Retenido (g)', validators=[DataRequired(), NumberRange(min=0)])

class FormularioTamizado(FlaskForm):
    peso_total_muestra = FloatField('Peso Total de Muestra (g)', validators=[DataRequired(), NumberRange(min=0.1)])
    mallas = FieldList(FormField(DatosMalla), min_entries=8)
    calcular = SubmitField('Calcular Análisis Granulométrico')
