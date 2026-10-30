-- ============================================================
-- Banco de dados: sistema_estoque
-- Sistema de gestão de estoque para pequenos comércios
-- ============================================================

CREATE DATABASE IF NOT EXISTS sistema_estoque
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sistema_estoque;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cargo ENUM('funcionario', 'administrador') NOT NULL DEFAULT 'funcionario',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria_id INT,
    quantidade INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 5,
    preco DECIMAL(10,2) NOT NULL,
    peso DECIMAL(10,3),
    unidade_peso ENUM('kg', 'l', 'ml') NOT NULL DEFAULT 'kg',
    data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_produto_categoria FOREIGN KEY (categoria_id)
        REFERENCES categorias(id) ON DELETE SET NULL,
    CONSTRAINT chk_quantidade_nao_negativa CHECK (quantidade >= 0),
    CONSTRAINT chk_preco_nao_negativo CHECK (preco >= 0)
);

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    usuario_id INT,
    tipo ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL,
    data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mov_produto FOREIGN KEY (produto_id)
        REFERENCES produtos(id) ON DELETE CASCADE,
    CONSTRAINT fk_mov_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id) ON DELETE SET NULL,
    CONSTRAINT chk_quantidade_mov_positiva CHECK (quantidade > 0)
);

CREATE INDEX idx_produtos_categoria ON produtos(categoria_id);
CREATE INDEX idx_mov_produto ON movimentacoes(produto_id);
CREATE INDEX idx_mov_data ON movimentacoes(data_movimentacao);

INSERT INTO categorias (nome) VALUES
    ('Alimentos'),
    ('Bebidas'),
    ('Limpeza'),
    ('Diversos');

-- Usuário administrador padrão, para o primeiro acesso ao sistema.
-- Login: admin@sistema.com | Senha: admin123 (trocar após o primeiro acesso)
INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES
('Administrador', 'admin@sistema.com', 'scrypt:32768:8:1$t4tCIT2wrzJPCqCY$5662e5320a824ebc3f617db4ba51872adae2ca8b3053b41f6f89d98b0355c134dd0c94f75af8da75c2478053c759edaf5bb2eb1f7e87607b8d1a7b4294b9b83d', 'administrador');