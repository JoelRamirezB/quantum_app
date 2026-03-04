from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_encript = db.Column(db.String(255), nullable=False) # Actualizado
    rol = db.Column(db.String(50), default='ADMINISTRATIVO')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación: Un usuario gestiona muchas facturas
    facturas_gestionadas = db.relationship('Factura', backref='gestor', lazy=True)

class ConfiguracionEmpresa(db.Model):
    __tablename__ = 'configuracion_empresa'
    
    id_config = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nit = db.Column(db.String(20), nullable=False)
    razon_social = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email_recepcion = db.Column(db.String(100))
    
    # Nuevos campos específicos para la API de SIIGO NUBE
    siigo_usuario = db.Column(db.String(100))
    siigo_llave_acceso = db.Column(db.Text)
    siigo_token_actual = db.Column(db.Text)
    
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación: Una empresa (configuración) es dueña de muchas facturas
    facturas_propiedad = db.relationship('Factura', backref='empresa', lazy=True)

class Factura(db.Model):
    __tablename__ = 'factura'
    
    # Restricción UNIQUE compuesta (Evita que se repita el Nro de factura del mismo proveedor)
    __table_args__ = (
        db.UniqueConstraint('numero_factura', 'nit_proveedor', name='uq_factura_proveedor'),
    )
    
    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_config = db.Column(db.Integer, db.ForeignKey('configuracion_empresa.id_config'))
    
    numero_factura = db.Column(db.String(50), nullable=False)
    nit_proveedor = db.Column(db.String(20), nullable=False) # Actualizado
    proveedor = db.Column(db.String(150))
    fecha_emision = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    moneda = db.Column(db.String(10), default='COP')
    subtotal = db.Column(db.Numeric(15, 2), default=0.00)
    total_impuestos = db.Column(db.Numeric(15, 2), default=0.00)
    total_pagar = db.Column(db.Numeric(15, 2), default=0.00)
    estado = db.Column(db.String(30), default='CARGADA') # Actualizado tamaño a 30
    ruta_archivo = db.Column(db.Text)
    
    # Campos para trazabilidad con SIIGO
    id_siigo = db.Column(db.String(100))
    mensaje_error = db.Column(db.Text)
    
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación: Una factura contiene muchos ítems (si se borra la factura, se borran los ítems)
    items = db.relationship('ItemFactura', backref='factura_padre', lazy=True, cascade="all, delete-orphan")

class ItemFactura(db.Model):
    __tablename__ = 'item_factura'
    
    id_item = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'), nullable=False)
    
    codigo_producto = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    cantidad = db.Column(db.Numeric(12, 4), nullable=False) # Actualizado precisión a 12,4
    valor_unitario = db.Column(db.Numeric(15, 2), nullable=False)
    porcentaje_impuesto = db.Column(db.Numeric(5, 2), default=0.00)
    valor_total = db.Column(db.Numeric(15, 2), default=0.00)