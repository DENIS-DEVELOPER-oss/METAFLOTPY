
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class FormularioValorizacion(FlaskForm):
    cantidad_concentrado = FloatField(
        'Cantidad de concentrado (Q) [t/mes]',
        validators=[DataRequired(), NumberRange(min=0.1)],
        render_kw={'placeholder': '500', 'step': '0.1'}
    )
    
    ley_metal = FloatField(
        'Ley del metal en el concentrado (L) [%]',
        validators=[DataRequired(), NumberRange(min=0.01, max=100)],
        render_kw={'placeholder': '28.0', 'step': '0.01'}
    )
    
    recuperacion = FloatField(
        'Recuperación metalúrgica (R) [%]',
        validators=[NumberRange(min=0, max=100)],
        render_kw={'placeholder': '95.0', 'step': '0.1', 'value': '95.0'}
    )
    
    precio_metal = FloatField(
        'Precio del metal (P) [USD/ton o USD/oz]',
        validators=[DataRequired(), NumberRange(min=0.01)],
        render_kw={'placeholder': '8500', 'step': '0.01'}
    )
    
    costo_tratamiento = FloatField(
        'Costo de tratamiento (C_tr) [USD/t concentrado]',
        validators=[NumberRange(min=0)],
        render_kw={'placeholder': '150', 'step': '0.01', 'value': '0'}
    )
    
    penalidades = FloatField(
        'Penalidades por impurezas (P_pen) [USD/t]',
        validators=[NumberRange(min=0)],
        render_kw={'placeholder': '20', 'step': '0.01', 'value': '0'}
    )
    
    factor_conversion = SelectField(
        'Factor de conversión según el metal (F)',
        choices=[
            ('31.1035', 'Oro: F = 31.1035 g/oz'),
            ('31.1035', 'Plata: F = 31.1035 g/oz'),
            ('1000', 'Cobre/Plomo/Zinc: F = 1000 kg/t')
        ],
        default='31.1035'
    )
    
    calcular = SubmitField('Calcular Valorización')
