from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena_encript = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('ADMINISTRADOR', 'OPERATIVO'), default='OPERATIVO') 
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    facturas_cargadas = db.relationship('Factura', foreign_keys='Factura.id_usuario_carga', backref='usuario_carga', lazy=True)
    facturas_validadas = db.relationship('Factura', foreign_keys='Factura.id_usuario_validador', backref='usuario_validador', lazy=True)
    auditorias = db.relationship('Auditoria', backref='usuario', lazy=True)


class ConfiguracionEmpresa(db.Model):
    __tablename__ = 'configuracion_empresa'
    
    id_config = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nit = db.Column(db.String(20), nullable=False)
    razon_social = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email_recepcion = db.Column(db.String(100))
    
    siigo_usuario = db.Column(db.String(100))
    siigo_llave_acceso = db.Column(db.Text)
    siigo_token_actual = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facturas_propiedad = db.relationship('Factura', backref='empresa', lazy=True)


class Factura(db.Model):
    __tablename__ = 'factura'

    __table_args__ = (
        db.UniqueConstraint('numero_factura', 'nit_proveedor', name='uq_factura_proveedor'),
        db.Index('idx_nit_proveedor', 'nit_proveedor'),
        db.Index('idx_fecha_emision', 'fecha_emision'),
        db.Index('idx_estado', 'estado'),
    )
    
    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario_carga = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_usuario_validador = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_config = db.Column(db.Integer, db.ForeignKey('configuracion_empresa.id_config'))
    
    numero_factura = db.Column(db.String(50), nullable=False)
    nit_proveedor = db.Column(db.String(20), nullable=False)
    proveedor = db.Column(db.String(150))
    tipo_factura = db.Column(db.String(20), default='COMPRA')
    metodo_pago = db.Column(db.String(50), default='Credito')
    
    fecha_emision = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    moneda = db.Column(db.String(10), default='COP')
    
    subtotal = db.Column(db.Numeric(15, 2), default=0.00)
    total_impuestos = db.Column(db.Numeric(15, 2), default=0.00)
    total_pagar = db.Column(db.Numeric(15, 2), default=0.00)
    
    estado = db.Column(db.String(30), default='CARGADA')
    ruta_archivo = db.Column(db.Text)
    id_siigo = db.Column(db.String(100))
    mensaje_error = db.Column(db.Text)
    
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_validacion = db.Column(db.DateTime)
    fecha_exportacion = db.Column(db.DateTime)

    items = db.relationship('ItemFactura', backref='factura_padre', lazy=True, cascade="all, delete-orphan")


class ItemFactura(db.Model):
    __tablename__ = 'item_factura'
    
    id_item = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('factura.id_factura'), nullable=False)
    
    codigo_producto = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    cantidad = db.Column(db.Numeric(12, 4), nullable=False)
    valor_unitario = db.Column(db.Numeric(15, 2), nullable=False)
    
    porcentaje_impuesto = db.Column(db.Numeric(5, 2), default=0.00)
    valor_impuesto = db.Column(db.Numeric(15, 2), default=0.00)
    valor_total = db.Column(db.Numeric(15, 2), default=0.00)

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    
    id_audit = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario')) 
    accion = db.Column(db.String(100), nullable=False)
    tabla_afectada = db.Column(db.String(50))
    id_referencia = db.Column(db.Integer)
    detalles = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)