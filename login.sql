-- Configuração de Data BR
SET DATESTYLE TO POSTGRES, DMY ;
SELECT current_date, current_timestamp ;

-- TABELA: entrada
DROP TABLE IF EXISTS entrada CASCADE;
CREATE TABLE entrada (
cod_usuario SERIAL PRIMARY KEY,
usuario VARCHAR(20) NOT NULL,
senha VARCHAR(10) NOT NULL,
);

-- POPULANDO entrada
SELECT * FROM entrada;
INSERT INTO entrada VALUES (default, 'haruka', '1008Liz'); 
INSERT INTO entrada VALUES (default, 'marly', 'Tapi1225');
INSERT INTO entrada VALUES (default, 'admin', 'admin01');