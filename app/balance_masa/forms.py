
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class FormularioBalanceMasa(FlaskForm):
    tipo_circuito = SelectField('Tipo de Circuito', 
                               choices=[
                                   ('directo', 'Circuito Cerrado Directo'),
                                   ('inverso', 'Circuito Cerrado Inverso'),
                                   ('sabc1', 'Circuito SABC-1'),
                                   ('sabc2', 'Circuito SABC-2')
                               ],
                               validators=[DataRequired()])
    
    # Campos para Circuito Directo (todos opcionales para permitir cálculos)
    f_alimentacion = FloatField('F: Flujo de alimentación (t/h)', 
                               validators=[Optional(), NumberRange(min=0.01)])
    p_producto = FloatField('P: Flujo del producto final (t/h)', 
                           validators=[Optional(), NumberRange(min=0.01)])
    r_rechazo = FloatField('R: Flujo del rechazo o carga circulante (t/h)', 
                          validators=[Optional(), NumberRange(min=0)])
    
    # Campos para Circuito Inverso
    f_alimentacion_inv = FloatField('F: Flujo de alimentación (t/h)', 
                                   validators=[Optional(), NumberRange(min=0.01)])
    r_rechazo_inv = FloatField('R: Flujo de rechazo antes del molino (t/h)', 
                              validators=[Optional(), NumberRange(min=0)])
    p_producto_inv = FloatField('P: Producto después del molino (t/h)', 
                               validators=[Optional(), NumberRange(min=0.01)])
    
    # Campos para SABC-1
    f_mineral_sabc1 = FloatField('F: Flujo de mineral nuevo (t/h)', 
                                validators=[Optional(), NumberRange(min=0.01)])
    s_producto_sag = FloatField('S: Producto del SAG (t/h)', 
                               validators=[Optional(), NumberRange(min=0.01)])
    b_producto_bolas = FloatField('B: Producto del molino de bolas (t/h)', 
                                 validators=[Optional(), NumberRange(min=0.01)])
    p_producto_final_sabc1 = FloatField('P: Producto final (t/h)', 
                                       validators=[Optional(), NumberRange(min=0.01)])
    r_carga_circulante_sabc1 = FloatField('R: Carga circulante (clasificador) (t/h)', 
                                         validators=[Optional(), NumberRange(min=0)])
    
    # Campos para SABC-2
    f_mineral_sabc2 = FloatField('F: Flujo de mineral nuevo (t/h)', 
                                validators=[Optional(), NumberRange(min=0.01)])
    s_producto_sag_sabc2 = FloatField('S: Producto del SAG (t/h)', 
                                     validators=[Optional(), NumberRange(min=0.01)])
    r_rechazo_sabc2 = FloatField('R: Flujo de rechazo al molino de bolas (t/h)', 
                                validators=[Optional(), NumberRange(min=0)])
    p_producto_final_sabc2 = FloatField('P: Producto final (t/h)', 
                                       validators=[Optional(), NumberRange(min=0.01)])
    
    calcular = SubmitField('Calcular Balance de Masa')
