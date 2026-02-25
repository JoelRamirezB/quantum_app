from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_ecpt = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='ADMINISTRATIVO')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    facturas_gestionadas = db.relationship('Factura', backref='gestor', lazy=True)

class ConfiguracionEmpresa(db.Model):
    __tablename__ = 'configuracion_empresa'
    id_config = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nit = db.Column(db.String(20), nullable=False)
    razon_social = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email_recepcion = db.Column(db.String(100))
    api_token_siigo = db.Column(db.Text)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    facturas_propiedad = db.relationship('Factura', backref='empresa', lazy=True)

class Factura(db.Model):
    __tablename__ = 'factura'
    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_config = db.Column(db.Integer, db.ForeignKey('configuracion_empresa.id_config'))
    numero_factura = db.Column(db.String(50))
    proveedor = db.Column(db.String(150))
    fecha_emision = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    moneda = db.Column(db.String(10), default='COP')
    subtotal = db.Column(db.Numeric(15, 2))
    total_impuestos = db.Column(db.Numeric(15, 2))
    total_pagar = db.Column(db.Numeric(15, 2))
    estado = db.Column(db.String(15), default='CARGADA')
    ruta_archivo = db.Column(db.Text)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('ItemFactura', backref='factura_padre', lazy=True, cascade="all, delete-orphan")

class ItemFactura(db.Model):
    __tablename__ = 'item_factura'
    id_item = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'), nullable=False)
    codigo_producto = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    cantidad = db.Column(db.Numeric(10, 2))
    valor_unitario = db.Column(db.Numeric(15, 2))
    porcentaje_impuesto = db.Column(db.Numeric(5, 2))
    valor_total = db.Column(db.Numeric(15, 2))
