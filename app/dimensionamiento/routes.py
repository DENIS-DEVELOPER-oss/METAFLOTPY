
from flask import Blueprint, render_template
from flask_login import login_required

bp_dimensionamiento = Blueprint('dimensionamiento', __name__)

@bp_dimensionamiento.route('/')
@login_required
def dimensionamiento():
    return render_template('dimensionamiento/dimensionamiento.html')

@bp_dimensionamiento.route('/molinos')
@login_required
def molinos():
    return render_template('dimensionamiento/molinos.html')

@bp_dimensionamiento.route('/celdas-flotacion')
@login_required
def celdas_flotacion():
    return render_template('dimensionamiento/celdas_flotacion.html')
