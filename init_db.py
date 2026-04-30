from dotenv import load_dotenv
load_dotenv()

from app import create_app, bcrypt, db
from app.models import Usuario

app = create_app()

with app.app_context():
    admin_existente = Usuario.query.filter_by(
        rol='ADMINISTRADOR').first()

    if admin_existente:
        print(f'Ya existe un administrador: '
              f'{admin_existente.email}')
        print('No se creó ningún usuario.')
    else:
        email = 'admin@atelcro.com'
        contrasena = 'Quantum2026'
        nombre = 'Administrador Quantum'

        hash_contrasena = bcrypt.generate_password_hash(
            contrasena).decode('utf-8')

        admin = Usuario(
            nombre_completo=nombre,
            email=email,
            contrasena_encript=hash_contrasena,
            rol='ADMINISTRADOR',
            activo=True
        )

        db.session.add(admin)
        db.session.commit()

        print('Usuario administrador creado exitosamente')
        print(f'Email: {email}')
        print(f'Contraseña inicial: {contrasena}')
        print('Cambia la contraseña después del primer ingreso.')