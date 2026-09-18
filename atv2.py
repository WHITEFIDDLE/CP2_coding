"""CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ip VARCHAR(16) UNIQUE,
    criticidade ENUM('baixa','media','alta')
);

CREATE TABLE ativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ativo_id INT NOT NULL,
    tipo VARCHAR(10) UNIQUE,
    severidade ENUM('baixa','media','alta'),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
);"""


ativos  = [(1,"SRV-WEB01","192.168.1.10","alta"), (2,"PC-RH03","192.168.1.45","baixa")]
alertas = [(1,1,"BRUTE_FORCE","critica"), (2,1,"PORT_SCAN","alta"), (3,2,"XSS","media")]

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha",
    database="seguranca"
)
