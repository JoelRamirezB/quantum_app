import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    PERMANENT_SESSION_LIFE = timedelta(minutes=30)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SIIGO_USUARIO = os.environ.get('SIIGO_USUARIO')
    SIIGO_LLAVE_ACCESO = os.environ.get('SIIGO_LLAVE_ACCESO')
    SIIGO_URL = os.environ.get('SIIGO_URL')
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'pool_timeout': 20,
        'pool_size': 5
    }

def init_app(app):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)