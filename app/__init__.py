from flask import Flask
from dotenv import load_dotenv
import os
from app.routes import main  # Importar el Blueprint de rutas

def create_app():
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Inicializar la aplicación Flask
    app = Flask(__name__)

    # Configuración de la aplicación (por ejemplo, clave secreta)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    # Registrar el Blueprint de rutas
    app.register_blueprint(main)

    return app
