CREATE DATABASE IF NOT EXISTS Quantum;
USE Quantum;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena_encript VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'ADMINISTRATIVO',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE configuracion_empresa (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(150) NOT NULL,
    direccion VARCHAR(200),        
    telefono VARCHAR(20),          
    email_recepcion VARCHAR(100),
    siigo_username VARCHAR(100), 
    siigo_access_key TEXT,
    siigo_token_actual TEXT,
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT, 
    id_config INT,  
    numero_factura VARCHAR(50) NOT NULL,
    nit_proveedor VARCHAR(20) NOT NULL, 
    proveedor VARCHAR(150),
    fecha_emision DATE,
    fecha_vencimiento DATE,       
    moneda VARCHAR(10) DEFAULT 'COP', 
    subtotal DECIMAL(15,2),        
    total_impuestos DECIMAL(15,2), 
    total_pagar DECIMAL(15,2),
    estado VARCHAR(30) DEFAULT 'CARGADA', 
    ruta_archivo TEXT,
    id_siigo VARCHAR(100), 
    mensaje_error TEXT,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP, 
   
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_config) REFERENCES configuracion_empresa(id_config),
    UNIQUE (numero_factura, nit_proveedor) 
);

CREATE TABLE item_factura (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL, 
    codigo_producto VARCHAR(50),    
    descripcion TEXT,
    cantidad DECIMAL(12,4),
    valor_unitario DECIMAL(15,2),
    porcentaje_impuesto DECIMAL(5,2), 
    valor_total DECIMAL(15,2),
    
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura) ON DELETE CASCADE
);
