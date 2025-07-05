
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp_principal = Blueprint('principal', __name__)

@bp_principal.route('/')
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for('principal.dashboard'))
    return render_template('principal/inicio.html')

@bp_principal.route('/dashboard')
@login_required
def dashboard():
    return render_template('principal/dashboard.html')
