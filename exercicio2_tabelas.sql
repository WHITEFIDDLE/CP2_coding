

# MySQL (crie e popule):
# ativos(id PK, nome, ip UNIQUE, criticidade ENUM('baixa','media','alta'))
# alertas(id PK, ativo_id FK, tipo, severidade, criado_em)

#ativos  = [(1,"SRV-WEB01","192.168.1.10","alta"), (2,"PC-RH03","192.168.1.45","baixa")]
#alertas = [(1,1,"BRUTE_FORCE","critica"), (2,1,"PORT_SCAN","alta"), (3,2,"XSS","media")]

# 1. Leia com um JOIN parametrizado.
# 2. Monte documentos assim e insira com insert_many:
# {"tipo":"BRUTE_FORCE","severidade":"critica",
#  "ativo":{"nome":"SRV-WEB01","ip":"192.168.1.10","criticidade":"alta"}}
# 3. Verifique a migração: conte no MySQL e no Mongo e compare.

# Saída esperada:
# MySQL: 3 alertas | MongoDB: 3 documentos -> MIGRAÇÃO ÍNTEGRA
# Consulta sem JOIN: db.alertas.find({"ativo.criticidade":"alta"}) -> 2 documentos
# Comentário (2 linhas): o que se ganha (leitura sem JOIN) e o que se perde
#                        (duplicação: renomear o ativo exige update_many).


CREATE TABLE alertas (
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
);

select * from ativos

