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
    return render_template('dashboard.html')