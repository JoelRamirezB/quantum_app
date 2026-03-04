CREATE DATABASE IF NOT EXISTS Quantum;
USE Quantum;

-- Tablas

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena_encript VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'ADMINISTRATIVO',
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
    ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

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
    subtotal DECIMAL(15,2) DEFAULT 0.00,        
    total_impuestos DECIMAL(15,2) DEFAULT 0.00, 
    total_pagar DECIMAL(15,2) DEFAULT 0.00,
    estado VARCHAR(30) DEFAULT 'CARGADA', 
    ruta_archivo TEXT,
    id_siigo VARCHAR(100), 
    mensaje_error TEXT,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP, 
   
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_config) REFERENCES configuracion_empresa(id_config),
    UNIQUE (numero_factura, nit_proveedor) -- Evita facturas duplicadas por proveedor
) ENGINE=InnoDB;

CREATE TABLE item_factura (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL, 
    codigo_producto VARCHAR(50),    
    descripcion TEXT,
    cantidad DECIMAL(12,4) NOT NULL,
    valor_unitario DECIMAL(15,2) NOT NULL,
    porcentaje_impuesto DECIMAL(5,2) DEFAULT 0.00, 
    valor_total DECIMAL(15,2) DEFAULT 0.00,
    
    FOREIGN KEY (id_factura) REFERENCES factura(id_factura) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Triggers

DELIMITER //

CREATE TRIGGER tg_item_total_insert BEFORE INSERT ON item_factura
FOR EACH ROW BEGIN
    SET NEW.valor_total = NEW.cantidad * NEW.valor_unitario;
END //

CREATE TRIGGER tg_item_total_update BEFORE UPDATE ON item_factura
FOR EACH ROW BEGIN
    SET NEW.valor_total = NEW.cantidad * NEW.valor_unitario;
END //

CREATE TRIGGER tg_factura_totales_insert AFTER INSERT ON item_factura
FOR EACH ROW BEGIN
    UPDATE factura SET 
        subtotal = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = NEW.id_factura),
        total_pagar = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = NEW.id_factura) + total_impuestos
    WHERE id_factura = NEW.id_factura;
END //

CREATE TRIGGER tg_factura_totales_update AFTER UPDATE ON item_factura
FOR EACH ROW BEGIN
    UPDATE factura SET 
        subtotal = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = NEW.id_factura),
        total_pagar = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = NEW.id_factura) + total_impuestos
    WHERE id_factura = NEW.id_factura;
END //

CREATE TRIGGER tg_factura_totales_delete AFTER DELETE ON item_factura
FOR EACH ROW BEGIN
    UPDATE factura SET 
        subtotal = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = OLD.id_factura),
        total_pagar = (SELECT IFNULL(SUM(valor_total), 0) FROM item_factura WHERE id_factura = OLD.id_factura) + total_impuestos
    WHERE id_factura = OLD.id_factura;
END //

DELIMITER ;

-- Procedimientos almacenados

DELIMITER //

CREATE PROCEDURE sp_crear_factura(
    IN p_id_usuario INT, IN p_id_config INT, IN p_num VARCHAR(50), 
    IN p_nit VARCHAR(20), IN p_prov VARCHAR(150), IN p_emision DATE, 
    IN p_impuestos DECIMAL(15,2), OUT p_id_out INT
)
BEGIN
    INSERT INTO factura (id_usuario, id_config, numero_factura, nit_proveedor, proveedor, fecha_emision, total_impuestos)
    VALUES (p_id_usuario, p_id_config, p_num, p_nit, p_prov, p_emision, p_impuestos);
    SET p_id_out = LAST_INSERT_ID();
END //

CREATE PROCEDURE sp_actualizar_siigo(
    IN p_id_factura INT, IN p_id_siigo VARCHAR(100), 
    IN p_estado VARCHAR(30), IN p_error TEXT
)
BEGIN
    UPDATE factura 
    SET id_siigo = p_id_siigo, estado = p_estado, mensaje_error = p_error
    WHERE id_factura = p_id_factura;
END //

CREATE PROCEDURE sp_obtener_pendientes()
BEGIN
    SELECT id_factura, numero_factura, proveedor, total_pagar 
    FROM factura 
    WHERE estado = 'CARGADA' OR estado = 'ERROR';
END //

DELIMITER ;

