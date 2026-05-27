CREATE DATABASE IF NOT EXISTS Quantum;
USE Quantum;

-- Tablas

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena_encript VARCHAR(255) NOT NULL, 
    rol ENUM('ADMINISTRADOR', 'OPERATIVO') DEFAULT 'OPERATIVO', 
    activo BOOLEAN DEFAULT TRUE, 
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE configuracion_empresa (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    nit VARCHAR(20) NOT NULL,
    razon_social VARCHAR(150) NOT NULL,
    direccion VARCHAR(200),        
    telefono VARCHAR(20),          
    email_recepcion VARCHAR(100),
    siigo_usuario VARCHAR(100), 
    siigo_llave_acceso TEXT,
    siigo_token_actual TEXT,
    activo BOOLEAN DEFAULT TRUE,
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_carga INT, 
    id_usuario_validador INT, 
    id_config INT,  
    numero_factura VARCHAR(50) NOT NULL,
    nit_proveedor VARCHAR(20) NOT NULL, 
    proveedor VARCHAR(150),
    tipo_factura ENUM('COMPRA', 'VENTA') DEFAULT 'COMPRA', 
    metodo_pago VARCHAR(50) DEFAULT 'Credito', 
    fecha_emision DATE,
    fecha_vencimiento DATE,       
    moneda VARCHAR(10) DEFAULT 'COP', 
    subtotal DECIMAL(15,2) DEFAULT 0.00,        
    total_impuestos DECIMAL(15,2) DEFAULT 0.00, 
    total_pagar DECIMAL(15,2) DEFAULT 0.00,
    estado ENUM('CARGADA', 'VALIDADA', 'EXPORTADA', 'ERROR') DEFAULT 'CARGADA',
    ruta_archivo TEXT,
    id_siigo VARCHAR(100), 
    mensaje_error TEXT,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP, 
    fecha_validacion DATETIME, 
    fecha_exportacion DATETIME,
   
    FOREIGN KEY (id_usuario_carga) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_usuario_validador) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_config) REFERENCES configuracion_empresa(id_config),
    UNIQUE (numero_factura, nit_proveedor),
    INDEX (nit_proveedor),
    INDEX (fecha_emision),
    INDEX (estado)
) ENGINE=InnoDB;

CREATE TABLE item_factura (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL, 
    codigo_producto VARCHAR(50),    
    descripcion TEXT,
    cantidad DECIMAL(12,4) NOT NULL,
    valor_unitario DECIMAL(15,2) NOT NULL,
    porcentaje_impuesto DECIMAL(5,2) DEFAULT 0.00, 
    valor_impuesto DECIMAL(15,2) DEFAULT 0.00,
    valor_total DECIMAL(15,2) DEFAULT 0.00,
    
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE auditoria (
    id_audit INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    accion VARCHAR(100) NOT NULL, 
    tabla_afectada VARCHAR(50),
    id_referencia INT,
    detalles TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Triggers

DELIMITER //

CREATE TRIGGER tg_item_calculos BEFORE INSERT ON item_factura
FOR EACH ROW BEGIN
    SET NEW.valor_impuesto = (NEW.cantidad * NEW.valor_unitario) * (NEW.porcentaje_impuesto / 100);
    SET NEW.valor_total = (NEW.cantidad * NEW.valor_unitario) + NEW.valor_impuesto;
END //

CREATE TRIGGER tg_factura_totales_update AFTER INSERT ON item_factura
FOR EACH ROW BEGIN
    UPDATE factura SET 
        subtotal = (SELECT IFNULL(SUM(cantidad * valor_unitario), 0) FROM item_factura WHERE id_factura = NEW.id_factura),
        total_impuestos = (SELECT IFNULL(SUM(valor_impuesto), 0) FROM item_factura WHERE id_factura = NEW.id_factura),
        total_pagar = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = NEW.id_factura)
    WHERE id_factura = NEW.id_factura;
END //

CREATE TRIGGER tg_proteccion_exportada BEFORE UPDATE ON factura
FOR EACH ROW BEGIN
    IF OLD.estado = 'EXPORTADA' AND NEW.estado = 'EXPORTADA' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Seguridad: No se permite editar una factura que ya fue EXPORTADA a SIIGO.';
    END IF;
END //

DELIMITER ;

-- Procedimientos almacenados   

DELIMITER //

CREATE PROCEDURE sp_crear_factura(
    IN p_user INT, IN p_config INT, IN p_num VARCHAR(50), 
    IN p_nit VARCHAR(20), IN p_prov VARCHAR(150), IN p_emision DATE, 
    IN p_vence DATE, IN p_moneda VARCHAR(10), OUT p_id_out INT
)
BEGIN
    INSERT INTO factura (id_usuario_carga, id_config, numero_factura, nit_proveedor, proveedor, fecha_emision, fecha_vencimiento, moneda)
    VALUES (p_user, p_config, p_num, p_nit, p_prov, p_emision, p_vence, p_moneda);
    SET p_id_out = LAST_INSERT_ID();
    
    INSERT INTO auditoria (id_usuario, accion, tabla_afectada, id_referencia, detalles)
    VALUES (p_user, 'CARGA PDF', 'factura', p_id_out, CONCAT('Factura número ', p_num));
END //

CREATE PROCEDURE sp_validar_factura(IN p_id_factura INT, IN p_user_validador INT)
BEGIN
    UPDATE factura SET 
        estado = 'VALIDADA', 
        id_usuario_validador = p_user_validador,
        fecha_validacion = NOW()
    WHERE id_factura = p_id_factura;
    
    INSERT INTO auditoria (id_usuario, accion, tabla_afectada, id_referencia, detalles)
    VALUES (p_user_validador, 'VALIDACIÓN DATOS', 'factura', p_id_factura, 'Usuario confirmó que los datos extraídos son correctos');
END //

CREATE PROCEDURE sp_obtener_para_siigo()
BEGIN
    SELECT numero_factura, nit_proveedor, proveedor, subtotal, total_impuestos, total_pagar, metodo_pago
    FROM factura WHERE estado = 'VALIDADA';
END //

DELIMITER ;