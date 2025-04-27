CREATE TABLE `solicitudes_compras` ( 
    `id` BIGINT NOT NULL AUTO_INCREMENT, 
    `negociador` VARCHAR(50), 
    `cuerpo_texto` TEXT, 
    `usuario_creador_solicitud` VARCHAR(50) NOT NULL, 
    `estado_solicitud` TINYINT(1) NOT NULL DEFAULT 1, 
    `estado` TINYINT(1) NOT NULL DEFAULT 1, 
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(), 
    PRIMARY KEY (`id`) 
); 

CREATE TABLE `solicitudes_compras_detalles` ( 
    `id` BIGINT NOT NULL AUTO_INCREMENT, 
    `solicitud_id` BIGINT NOT NULL, 
    `referencia` VARCHAR(50), 
    `producto` TEXT, 
    `cantidad` INT(10), 
    `proveedor` TEXT, 
    `marca` VARCHAR(50), 
    `estado` TINYINT(1) NOT NULL DEFAULT 1, 
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(), 
    PRIMARY KEY (`id`) 
); 

ALTER TABLE `solicitudes_compras_detalles` 
ADD FOREIGN KEY (`solicitud_id`) 
REFERENCES `solicitudes_compras`(`id`) ON UPDATE CASCADE ON DELETE RESTRICT; 