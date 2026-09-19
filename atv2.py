from pymongo import MongoClient
import mysql.connector
from mysql.connector import Error

conexao = None
cliente_mongo = None

#====================================================

#Criando as tabelas pedidas no exercicio.
"""CREATE TABLE ativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ip VARCHAR(45) UNIQUE NOT NULL,
    criticidade ENUM('baixa', 'media', 'alta') NOT NULL
);

CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ativo_id INT NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    severidade VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
);"""

#====================================================

# Populando o banco MySQL com dados da atividade
"""INSERT INTO ativos (id, nome, ip, criticidade)
VALUES
    (1, 'SRV-WEB01', '192.168.1.10', 'alta'),
    (2, 'PC-RH03', '192.168.1.45', 'baixa');

INSERT INTO alertas (id, ativo_id, tipo, severidade)
VALUES
    (1, 1, 'BRUTE_FORCE', 'critica'),
    (2, 1, 'PORT_SCAN', 'alta'),
    (3, 2, 'XSS', 'media');"""

#====================================================

try:
    # Conexão MySQL
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="senha",
        database="seguranca"
    )

    print("Conectado ao MySQL!")

    # dictionary=True permite linha["tipo"]
    cursor = conexao.cursor(dictionary=True)

    consulta = """
        SELECT
            al.tipo,
            al.severidade,
            at.nome,
            at.ip,
            at.criticidade
        FROM alertas AS al
        INNER JOIN ativos AS at
            ON al.ativo_id = at.id
        WHERE al.id >= %s
    """

    cursor.execute(consulta, (1,))
    resultados = cursor.fetchall()

    documentos = []

    for linha in resultados:
        documento = {
            "tipo": linha["tipo"],
            "severidade": linha["severidade"],
            "ativo": {
                "nome": linha["nome"],
                "ip": linha["ip"],
                "criticidade": linha["criticidade"]
            }
        }

        documentos.append(documento)

    cliente_mongo = MongoClient("mongodb://localhost:27017/")
    banco_mongo = cliente_mongo["seguranca"]
    colecao_alertas = banco_mongo["alertas"]

    # Limpa a coleção para não duplicar ao executar novamente
    colecao_alertas.delete_many({})

    if documentos:
        resultado_mongo = colecao_alertas.insert_many(documentos)

        print(
            f"Documentos inseridos: "
            f"{len(resultado_mongo.inserted_ids)}"
        )

    cursor.execute("SELECT COUNT(*) AS total FROM alertas")
    total_mysql = cursor.fetchone()["total"]

    total_mongo = colecao_alertas.count_documents({})

    if total_mysql == total_mongo:
        status = "MIGRAÇÃO ÍNTEGRA"
    else:
        status = "MIGRAÇÃO FALHA"

    print(
        f"MySQL: {total_mysql} alertas | "
        f"MongoDB: {total_mongo} documentos -> {status}"
    )

except Error as erro:
    print(f"Erro no MySQL: {erro}")

except Exception as erro:
    print(f"Erro durante a migração: {erro}")

finally:
    if conexao is not None and conexao.is_connected():
        cursor.close()
        conexao.close()

    if cliente_mongo is not None:
        cliente_mongo.close()