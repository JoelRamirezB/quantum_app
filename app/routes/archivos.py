import os
from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required

archivos = Blueprint('archivos', __name__)

@archivos.route('/uploads/<nombre_archivo>')
@login_required
def servir_archivo(nombre_archivo):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], nombre_archivo)