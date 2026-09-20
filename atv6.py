"""CREATE TABLE analistas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    nivel INT NOT NULL
    );"""

"""CREATE TABLE incidentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dono_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    severidade ENUM('baixa', 'media', 'alta', 'critica') NOT NULL,
    status ENUM('aberto', 'em andamento', 'resolvido') NOT NULL,
    FOREIGN KEY (dono_id) REFERENCES analistas(id)
);"""

"""INSERT INTO analistas (id, nome, api_key, nivel)
VALUES
    (1, 'ana', 'key-ana-001', 5),
    (2, 'bruno', 'key-bruno-002', 2);

INSERT INTO incidentes (
    id,
    dono_id,
    titulo,
    severidade,
    status
)
VALUES
    (1, 1, 'Brute force SSH', 'critica', 'aberto'),
    (2, 2, 'Phishing no RH', 'media', 'aberto');"""

from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def conectar_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="senha",
        database="seguranca"
    )

def autenticar():

    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return None

    conexao = conectar_mysql()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""SELECT id, nome, nivel FROM analistas WHERE api_key = %s""", (api_key,))

    analista = cursor.fetchone()

    cursor.close()
    conexao.close()

    return analista

@app.get("/api/incidentes/<int:incidente_id>")
def get_incidentes(incidente_id):
    analista = autenticar()

    if analista is None:
        return jsonify({"error": "Autenticação falhou"}), 401

    conexao = conectar_mysql()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM incidentes WHERE id = %s", (incidente_id,))
    incidente = cursor.fetchone()

    cursor.close()
    conexao.close()

    if incidente is None:
        return jsonify({
            "erro": "incidente não encontrado"
        }), 404

    if incidente["dono_id"] != analista["id"]:
        return jsonify({
            "erro": "acesso negado"
        }), 403

    return jsonify(incidente), 200
    
if __name__ == "__main__":
    app.run()