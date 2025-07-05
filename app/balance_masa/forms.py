
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FormularioBalanceMasa(FlaskForm):
    alimentacion_fresca = FloatField('Alimentación Fresca (t/h)', validators=[DataRequired(), NumberRange(min=0.1)])
    razon_carga_circulante = FloatField('Razón de Carga Circulante', validators=[DataRequired(), NumberRange(min=0)])
    eficiencia_clasificador = FloatField('Eficiencia del Clasificador (%)', validators=[DataRequired(), NumberRange(min=1, max=99)])
    calcular = SubmitField('Calcular Balance de Masa')
