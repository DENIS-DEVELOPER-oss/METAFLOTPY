
from flask import Blueprint, render_template
from flask_login import login_required

bp_valorizacion = Blueprint('valorizacion', __name__)

@bp_valorizacion.route('/')
@login_required
def valorizacion():
    return render_template('valorizacion/valorizacion.html')
