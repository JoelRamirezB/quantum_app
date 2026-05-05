from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import ConfiguracionEmpresa, Auditoria

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

@configuracion.route('/configuracion/test-siigo')
@login_required
@solo_admin
def test_siigo():
    from app.services.siigo_service import SiigoService
    try:
        siigo = SiigoService()
        token = siigo.obtener_token()

        if not token:
            return jsonify({
                'exito': False,
                'mensaje': 'No se pudo obtener el token de SIIGO'
            })

        comprobantes = siigo.obtener_tipos_comprobante()
        usuarios = siigo.obtener_usuarios()
        impuestos = siigo.obtener_impuestos()

        return jsonify({
            'exito': True,
            'mensaje': 'Conexion exitosa con SIIGO NUBE',
            'datos': {
                'comprobantes': len(comprobantes) if comprobantes else 0,
                'usuarios': len(usuarios) if usuarios else 0,
                'impuestos': len(impuestos) if impuestos else 0,
                'empresa': 'Atelcro S.A.S'
            }
        })

    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error de conexion: {str(e)}'
        })

@configuracion.route('/usuarios')
@login_required
@solo_admin
def lista_usuarios():
    from app.models import Usuario
    usuarios = Usuario.query.order_by(
        Usuario.fecha_creacion.desc()).all()
    return render_template('usuarios.html', usuarios=usuarios)

@configuracion.route('/usuarios/<int:id_usuario>/reset', methods=['POST'])
@login_required
@solo_admin
def reset_password(id_usuario):
    from app.models import Usuario
    from app import bcrypt

    usuario = Usuario.query.get_or_404(id_usuario)

    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes resetear tu propia contraseña ' 'desde aquí.', 'warning')
        return redirect(url_for('configuracion.lista_usuarios'))

    nueva_password = 'Quantum2026'
    hash_password = bcrypt.generate_password_hash(nueva_password).decode('utf-8')
    usuario.contrasena_encript = hash_password
    db.session.commit()

    db.session.add(Auditoria(
        id_usuario=current_user.id_usuario,
        accion='RESET_PASSWORD',
        tabla_afectada='usuario',
        id_referencia=usuario.id_usuario,
        detalles=f'Contraseña reseteada para '
                 f'{usuario.email}'
    ))
    db.session.commit()

    flash(f'Contraseña de {usuario.nombre_completo} ' f'reseteada a Quantum2026.', 'success')
    return redirect(url_for('configuracion.lista_usuarios'))