-- ================================
-- BANCO: intuitive_care
-- ================================

CREATE DATABASE IF NOT EXISTS intuitive_care
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE intuitive_care;

-- ================================
-- TABELA: operadoras (dados cadastrais)
-- ================================
CREATE TABLE IF NOT EXISTS operadoras (
    registro_ans VARCHAR(20),      
    cnpj VARCHAR(20),              
    razao_social VARCHAR(255),     
    modalidade VARCHAR(100),      
    uf CHAR(2),                    
    PRIMARY KEY (registro_ans)     
);

CREATE INDEX idx_operadoras_uf ON operadoras (uf);

-- ================================
-- TABELA: despesas_consolidadas
-- ================================
CREATE TABLE IF NOT EXISTS despesas_consolidadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social VARCHAR(255),
    registro_ans VARCHAR(20),
    modalidade VARCHAR(100),
    uf CHAR(2),
    ano INT,
    trimestre VARCHAR(20),
    valor_despesas DECIMAL(18,2),
    razao_social_valida BOOLEAN,
    valor_valido BOOLEAN,
    cnpj_limpo VARCHAR(20),
    cnpj_valido BOOLEAN
);

CREATE INDEX idx_despesas_uf ON despesas_consolidadas (uf);
CREATE INDEX idx_despesas_ano_trim ON despesas_consolidadas (ano, trimestre);

-- ================================
-- TABELA: despesas_agregadas
-- ================================
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas DECIMAL(18,2),
    media_trimestral DECIMAL(18,2),
    desvio_padrao DECIMAL(18,2)
);

CREATE INDEX idx_agregadas_uf ON despesas_agregadas (uf);
