import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    PERMANENT_SESSION_LIFE = timedelta(minutes=30)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  

def init_app(app):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)