
from flask import Blueprint, render_template

bp_valorizacion = Blueprint('valorizacion', __name__)

@bp_valorizacion.route('/')
def valorizacion():
    return render_template('valorizacion/valorizacion.html')
