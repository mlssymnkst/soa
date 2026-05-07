
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
INSERT INTO entrada VALUES (default, 'haruka', 'Liz06122025'); 
INSERT INTO entrada VALUES (default, 'marly', 'Tapi1112');
INSERT INTO entrada VALUES (default, 'admin', 'admin01');
INSERT INTO entrada VALUES (default, 'luiz', '12345');
INSERT INTO entrada VALUES (default, 'gustavo', '5678910');
INSERT INTO entrada VALUES (default, 'melissa', '150125');
INSERT INTO entrada VALUES (default, 'mariana', '67676767');
INSERT INTO entrada VALUES (default, 'ramon', '1617181920');