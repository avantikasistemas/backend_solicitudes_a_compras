CREATE TABLE solicitudes_compras (
    id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    negociador VARCHAR(50) NULL,
    cuerpo_texto TEXT NULL,
    usuario_creador_solicitud VARCHAR(50) NOT NULL,
    estado_solicitud TINYINT NOT NULL DEFAULT 1,
    estado TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE solicitudes_compras_detalles (
    id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    solicitud_id BIGINT NOT NULL,
    referencia VARCHAR(50) NULL,
    producto TEXT NULL,
    cantidad INT NULL,
    proveedor TEXT NULL,
    marca VARCHAR(50) NULL,
    estado TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

ALTER TABLE solicitudes_compras_detalles
ADD CONSTRAINT FK_solicitudes_compras_detalles_solicitud_id
FOREIGN KEY (solicitud_id)
REFERENCES solicitudes_compras(id)
ON UPDATE CASCADE ON DELETE NO ACTION;