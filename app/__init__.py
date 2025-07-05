from flask import Flask

def crear_aplicacion():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-metaflotpy-2024'

    # Registrar blueprints (sin autenticación)
    from app.tamizado.routes import bp_tamizado
    from app.balance_masa.routes import bp_balance_masa
    from app.balance_metalurgico.routes import bp_balance_metalurgico
    from app.dimensionamiento.routes import bp_dimensionamiento
    from app.valorizacion.routes import bp_valorizacion
    from app.utilitarios.routes import bp_utilitarios
    from app.principal.routes import bp_principal

    app.register_blueprint(bp_principal)
    app.register_blueprint(bp_tamizado, url_prefix='/tamizado')
    app.register_blueprint(bp_balance_masa, url_prefix='/balance-masa')
    app.register_blueprint(bp_balance_metalurgico, url_prefix='/balance-metalurgico')
    app.register_blueprint(bp_dimensionamiento, url_prefix='/dimensionamiento')
    app.register_blueprint(bp_valorizacion, url_prefix='/valorizacion')
    app.register_blueprint(bp_utilitarios, url_prefix='/utilitarios')

    return app