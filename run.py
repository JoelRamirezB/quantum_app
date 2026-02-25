from app import create_app, db

from app.models import Usuario, ConfiguracionEmpresa, Factura, ItemFactura

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos 'Quantum' conectada y tablas verificadas.")
    
    print("Iniciando servidor Quantum...")
    app.run(debug=True, port=5000)