
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FormularioBalanceMetalurgico(FlaskForm):
    ley_alimentacion = FloatField('Ley de Alimentación (%)', validators=[DataRequired(), NumberRange(min=0.01, max=100)])
    ley_concentrado = FloatField('Ley del Concentrado (%)', validators=[DataRequired(), NumberRange(min=0.01, max=100)])
    ley_relave = FloatField('Ley del Relave (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    razon_concentracion = FloatField('Razón de Concentración', validators=[DataRequired(), NumberRange(min=1)])
    calcular = SubmitField('Calcular Balance Metalúrgico')
