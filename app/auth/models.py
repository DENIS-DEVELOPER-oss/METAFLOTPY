
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre_usuario, email, hash_contrasena):
        self.id = id_usuario
        self.nombre_usuario = nombre_usuario
        self.email = email
        self.hash_contrasena = hash_contrasena
    
    def verificar_contrasena(self, contrasena):
        return check_password_hash(self.hash_contrasena, contrasena)
    
    @staticmethod
    def obtener(id_usuario):
        # Base de datos simple en memoria para demo
        usuarios_demo = {
            '1': Usuario('1', 'admin', 'admin@metaflotpy.com', 
                        generate_password_hash('admin123'))
        }
        return usuarios_demo.get(id_usuario)
    
    @staticmethod
    def obtener_por_nombre_usuario(nombre_usuario):
        if nombre_usuario == 'admin':
            return Usuario('1', 'admin', 'admin@metaflotpy.com', 
                          generate_password_hash('admin123'))
        return None
