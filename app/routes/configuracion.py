from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import ConfiguracionEmpresa

configuracion = Blueprint('configuracion', __name__)

def solo_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'ADMINISTRADOR':
            flash('No tienes permiso para acceder a esta sección', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@configuracion.route('/configuracion', methods=['GET', 'POST'])
@login_required
@solo_admin
def ver_configuracion():
    config = ConfiguracionEmpresa.query.filter_by(activo=True).first()

    if request.method == 'POST':
        
        nit = request.form.get('nit') or ''
        razon_social = request.form.get('razon_social') or ''

        if not nit or not razon_social:
            flash('El NIT y la razón social son obligatorios', 'danger')
            return redirect(url_for('configuracion.ver_configuracion'))

        if config is None:
            config = ConfiguracionEmpresa()
            db.session.add(config)

        config.nit = nit.strip()
        config.razon_social = razon_social.strip()

        direccion = request.form.get('direccion') or ''
        config.direccion = direccion.strip() if direccion.strip() else None

        telefono = request.form.get('telefono') or ''
        config.telefono = telefono.strip() if telefono.strip() else None

        email = request.form.get('email_recepcion') or ''
        config.email_recepcion = email.strip() if email.strip() else None

        siigo_usuario = request.form.get('siigo_usuario') or ''
        config.siigo_usuario = siigo_usuario.strip() if siigo_usuario.strip() else None

        siigo_llave = request.form.get('siigo_llave_acceso') or ''
        if siigo_llave.strip():
            config.siigo_llave_acceso = siigo_llave.strip()

        config.activo = True
        db.session.commit()
        flash('Configuración guardada exitosamente', 'success')
        return redirect(url_for('configuracion.ver_configuracion'))

    return render_template('configuracion.html', config=config)