
from flask import Flask
from flask_login import LoginManager
import os

def crear_aplicacion():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'clave-secreta-metaflotpy-2024'
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.iniciar_sesion'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def cargar_usuario(id_usuario):
        from app.auth.models import Usuario
        return Usuario.obtener(id_usuario)
    
    # Registrar blueprints
    from app.auth.routes import bp_auth
    from app.tamizado.routes import bp_tamizado
    from app.balance_masa.routes import bp_balance_masa
    from app.balance_metalurgico.routes import bp_balance_metalurgico
    from app.dimensionamiento.routes import bp_dimensionamiento
    from app.valorizacion.routes import bp_valorizacion
    from app.utilitarios.routes import bp_utilitarios
    from app.principal.routes import bp_principal
    
    app.register_blueprint(bp_principal)
    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_tamizado, url_prefix='/tamizado')
    app.register_blueprint(bp_balance_masa, url_prefix='/balance-masa')
    app.register_blueprint(bp_balance_metalurgico, url_prefix='/balance-metalurgico')
    app.register_blueprint(bp_dimensionamiento, url_prefix='/dimensionamiento')
    app.register_blueprint(bp_valorizacion, url_prefix='/valorizacion')
    app.register_blueprint(bp_utilitarios, url_prefix='/utilitarios')
    
    return app
