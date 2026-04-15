from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder.'

    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.routes.configuracion import configuracion as configuracion_blueprint
    app.register_blueprint(configuracion_blueprint)

    from app.routes.carga import carga as carga_blueprint
    app.register_blueprint(carga_blueprint)

    from app.routes.validacion import validacion as validacion_blueprint
    app.register_blueprint(validacion_blueprint)

    from app.routes.archivos import archivos as archivos_blueprint
    app.register_blueprint(archivos_blueprint)

    from app.routes.historial import historial as historial_blueprint
    app.register_blueprint(historial_blueprint)

    from app.routes.exportacion import exportacion as exportacion_blueprint
    app.register_blueprint(exportacion_blueprint)

    return app