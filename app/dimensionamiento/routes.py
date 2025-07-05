
from flask import Blueprint, render_template

bp_dimensionamiento = Blueprint('dimensionamiento', __name__)

@bp_dimensionamiento.route('/')
def dimensionamiento():
    return render_template('dimensionamiento/dimensionamiento.html')

@bp_dimensionamiento.route('/molinos')
def molinos():
    return render_template('dimensionamiento/molinos.html')

@bp_dimensionamiento.route('/celdas-flotacion')
def celdas_flotacion():
    return render_template('dimensionamiento/celdas_flotacion.html')
