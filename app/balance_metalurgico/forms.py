
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class FormularioBalanceMetalurgico(FlaskForm):
    tipo_balance = SelectField('Tipo de Balance', 
                              choices=[
                                  ('1_concentrado', 'Balance Metalúrgico - 1 Concentrado'),
                                  ('2_concentrados', 'Balance Metalúrgico - 2 Concentrados'),
                                  ('3_concentrados', 'Balance Metalúrgico - 3 Concentrados')
                              ],
                              default='1_concentrado')
    
    # Campos para Balance 1 Concentrado
    f_masa_alimentacion = FloatField('F: Masa de alimentación (t/día o t/h)', validators=[Optional(), NumberRange(min=0)])
    c_masa_concentrado = FloatField('C: Masa de concentrado', validators=[Optional(), NumberRange(min=0)])
    t_masa_relave = FloatField('T: Masa de relave', validators=[Optional(), NumberRange(min=0)])
    f_ley_alimentacion = FloatField('f: Ley de alimentación (% o g/t)', validators=[Optional(), NumberRange(min=0)])
    c_ley_concentrado = FloatField('c: Ley de concentrado', validators=[Optional(), NumberRange(min=0)])
    t_ley_relave = FloatField('t: Ley de relave', validators=[Optional(), NumberRange(min=0)])
    
    # Campos para Balance 2 Concentrados
    c1_masa_concentrado1 = FloatField('C₁: Masa de concentrado 1', validators=[Optional(), NumberRange(min=0)])
    c2_masa_concentrado2 = FloatField('C₂: Masa de concentrado 2', validators=[Optional(), NumberRange(min=0)])
    c1_ley_concentrado1 = FloatField('c₁: Ley de concentrado 1', validators=[Optional(), NumberRange(min=0)])
    c2_ley_concentrado2 = FloatField('c₂: Ley de concentrado 2', validators=[Optional(), NumberRange(min=0)])
    
    # Campos para Balance 3 Concentrados
    c3_masa_concentrado3 = FloatField('C₃: Masa de concentrado 3', validators=[Optional(), NumberRange(min=0)])
    c3_ley_concentrado3 = FloatField('c₃: Ley de concentrado 3', validators=[Optional(), NumberRange(min=0)])
    
    calcular = SubmitField('Calcular Balance Metalúrgico')
