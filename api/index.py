# api/index.py

from main import app  # Importa la app Flask desde app/main.py

def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)
