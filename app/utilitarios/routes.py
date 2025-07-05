
from flask import Blueprint, render_template
from flask_login import login_required

bp_utilitarios = Blueprint('utilitarios', __name__)

@bp_utilitarios.route('/')
@login_required
def utilitarios():
    return render_template('utilitarios/utilitarios.html')

@bp_utilitarios.route('/conversores')
@login_required
def conversores():
    return render_template('utilitarios/conversores.html')
