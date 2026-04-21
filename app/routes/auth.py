from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import Usuario

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and bcrypt.check_password_hash(usuario.contrasena_encript, password):
            if not usuario.activo:
                flash('Tu cuenta está desactivada', 'danger')
                return redirect(url_for('auth.login'))
            login_user(usuario)
            session.permanent = True
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')            
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/')
@login_required
def dashboard():

    from app.models import Factura

    total_facturas = Factura.query.count()
    pendientes = Factura.query.filter_by(estado='CARGADA').count()
    validadas = Factura.query.filter_by(estado='VALIDADA').count()
    exportadas = Factura.query.filter_by(estado='EXPORTADA').count()
    ultimas_facturas =  Factura.query.order_by(Factura.fecha_carga.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_facturas=total_facturas,
        pendientes=pendientes,
        validadas=validadas,
        exportadas=exportadas,
        ultimas_facturas=ultimas_facturas
    )