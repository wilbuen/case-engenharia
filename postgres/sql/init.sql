CREATE TABLE condominios (
    condominio_id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco TEXT NOT NULL
);

CREATE TABLE moradores (
    morador_id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    condominio_id INT NOT NULL,
    data_registro DATE NOT NULL,
    FOREIGN KEY (condominio_id) REFERENCES condominios(condominio_id)
);

CREATE TABLE imoveis (
    imovel_id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    condominio_id INT NOT NULL,
    valor NUMERIC(15, 2) NOT NULL,
    FOREIGN KEY (condominio_id) REFERENCES condominios(condominio_id)
);

CREATE TABLE transacoes (
    transacao_id SERIAL PRIMARY KEY,
    imovel_id INT NOT NULL,
    morador_id INT NOT NULL,
    data_transacao DATE NOT NULL,
    valor_transacao NUMERIC(15, 2) NOT NULL,
    FOREIGN KEY (imovel_id) REFERENCES imoveis(imovel_id),
    FOREIGN KEY (morador_id) REFERENCES moradores(morador_id)
);