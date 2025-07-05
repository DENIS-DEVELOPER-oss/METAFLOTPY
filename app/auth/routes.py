
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.auth.forms import FormularioInicioSesion, FormularioRegistro
from app.auth.models import Usuario

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/iniciar-sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    formulario = FormularioInicioSesion()
    if formulario.validate_on_submit():
        usuario = Usuario.obtener_por_nombre_usuario(formulario.nombre_usuario.data)
        if usuario and usuario.verificar_contrasena(formulario.contrasena.data):
            login_user(usuario)
            return redirect(url_for('principal.dashboard'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('auth/iniciar_sesion.html', formulario=formulario)

@bp_auth.route('/cerrar-sesion')
@login_required
def cerrar_sesion():
    logout_user()
    return redirect(url_for('principal.inicio'))

@bp_auth.route('/registro', methods=['GET', 'POST'])
def registro():
    formulario = FormularioRegistro()
    if formulario.validate_on_submit():
        flash('Registro exitoso! Por favor inicia sesión.')
        return redirect(url_for('auth.iniciar_sesion'))
    return render_template('auth/registro.html', formulario=formulario)
