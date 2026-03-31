from app import create_app, db, bcrypt
from app.models import Usuario

app = create_app()

with app.app_context():
    password_hash = bcrypt.generate_password_hash(
                    'admin123').decode('utf-8')
    
    usuario = Usuario(
        nombre_completo='Administrador Quantum',
        email='admin@quantum.com',
        contrasena_encript=password_hash,
        rol='ADMINISTRADOR',
        activo=True
    )
    
    db.session.add(usuario)
    db.session.commit()
    print('Usuario administrador creado exitosamente.')