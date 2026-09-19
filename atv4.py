"""CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    nivel_acesso INT NOT NULL
);"""

"""INSERT INTO usuarios (id, nome, email, nivel_acesso)
VALUES
    (1, 'ana', 'ana@x.com', 5),
    (2, 'bruno', 'bruno@x.com', 2),
    (3, 'caio', 'caio@x.com', 1);"""

import mysql.connector
from pymongo import MongoClient
from datetime import datetime



conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha",
    database="seguranca"
)

cursor = conexao.cursor(dictionary=True)

cliente_mongo = MongoClient("mongodb://localhost:27017/")
auditoria = cliente_mongo["seguranca"]["auditoria"]

def alterar_nivel(admin_id, alvo_id, novo_nivel):
    cursor.execute("SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = %s", (admin_id,))
    admin = cursor.fetchone()
    cursor.execute("SELECT id, nome, email, nivel_acesso FROM usuarios WHERE id = %s", (alvo_id,))
    alvo = cursor.fetchone()

    print("Administrador:", admin)
    print("Alvo:", alvo)

    if admin is None or alvo is None:
        print("Erro: Usuário administrador ou alvo não encontrado.")
        conexao.rollback()
        resultado = "RECUSADO"
        motivo = "usuário administrador ou alvo não encontrado"

    elif int(admin['nivel_acesso']) < 5:
        print("Erro: O usuário não tem permissão para alterar níveis de acesso.")
        conexao.rollback()
        resultado = "RECUSADO"
        motivo = "usuário sem permissão para alterar níveis"

    elif admin == alvo:
        print("Erro: Um usuário não pode alterar seu próprio nível de acesso.")
        conexao.rollback()
        resultado = "RECUSADO"
        motivo = "usuário tentou alterar seu próprio nível"
    else:
        cursor.execute("UPDATE usuarios SET nivel_acesso = %s WHERE id = %s", (novo_nivel, alvo_id))
        conexao.commit()
        resultado = "OK"
        motivo = "nível alterado"
        
    auditoria.insert_one({
            "admin_id": admin_id,
            "alvo_id": alvo_id,
            "nivel_novo": novo_nivel,
            "resultado": resultado,
            "timestamp": datetime.now()
        })

    print(
            f"{resultado}: admin={admin_id}, alvo={alvo_id}, "
            f"novo nível: {novo_nivel}. {motivo}"
        )

alterar_nivel(1, 2, 4)
alterar_nivel(2, 3, 5)
alterar_nivel(1, 1, 9)
alterar_nivel(1, 99, 3)

cursor.execute(
    "SELECT id, nome, nivel_acesso FROM usuarios ORDER BY id"
)

for usuario in cursor.fetchall():
    print(usuario)

total = auditoria.count_documents({})
recusadas = auditoria.count_documents({
    "resultado": "RECUSADO"
})

print(f"Total de auditorias: {total}")
print(f"Tentativas recusadas: {recusadas}")


