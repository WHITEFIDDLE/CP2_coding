"""CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    severidade ENUM(
        'baixa',
        'media',
        'alta',
        'critica'
    ) NOT NULL,
    ip_origem VARCHAR(45) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""

""""INSERT INTO eventos (tipo, severidade, ip_origem, criado_em)
VALUES
    ('LOGIN_FAIL',  'media',   '192.168.1.10', '2026-09-19 08:00:00'),
    ('PORT_SCAN',   'alta',    '192.168.1.20', '2026-09-19 08:10:00'),
    ('BRUTE_FORCE', 'critica', '192.168.1.30', '2026-09-19 08:20:00'),
    ('XSS',         'media',   '192.168.1.40', '2026-09-19 08:30:00'),
    ('SQLI',        'critica', '192.168.1.50', '2026-09-19 08:40:00'),
    ('LOGIN_FAIL',  'baixa',   '192.168.1.60', '2026-09-19 08:50:00'),
    ('PORT_SCAN',   'alta',    '192.168.1.70', '2026-09-19 09:00:00'),
    ('BRUTE_FORCE', 'critica', '192.168.1.80', '2026-09-19 09:10:00'),
    ('XSS',         'media',   '192.168.1.90', '2026-09-19 09:20:00'),
    ('SQLI',        'alta',    '192.168.1.100','2026-09-19 09:30:00');"""

from flask import Flask, jsonify, request
import mysql.connector


app = Flask(__name__)


conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="senha",
        database="seguranca"
    )

print("Conectado ao MySQL!")


cursor = conexao.cursor()

@app.get("/api/eventos")
def get_eventos():
    ordenar_por = request.args.get("ordenar_por", "data")
    ordem = request.args.get("ordem", "desc")
    tamanho_texto = request.args.get("tamanho", "20")

    if ordenar_por not in COLUNAS:
        return jsonify({"erro": "Parâmetro 'ordenar_por' inválido"}), 400

    elif ordem not in ORDENS:
        return jsonify({"erro": "Parâmetro 'ordem' inválido"}), 400

    elif not tamanho_texto.isdigit() or int(tamanho_texto) <= 0 or int(tamanho_texto) > 1000:
        return jsonify({"erro": "Parâmetro 'tamanho' inválido"}), 400

    try:
        tamanho = int(tamanho_texto)
    except ValueError:
        return jsonify({
            "erro": "tamanho deve ser inteiro"
        }), 400

    coluna_sql = COLUNAS[ordenar_por]
    ordem_sql = ORDENS[ordem]

    cursor.execute(f"SELECT * FROM eventos ORDER BY {coluna_sql} {ordem_sql} LIMIT %s", (tamanho,))
    eventos = cursor.fetchall()
    return jsonify(eventos) 

    cursor.close()
    conexao.close()

COLUNAS = {
    "data": "criado_em",
    "sev": "severidade",
    "ip": "ip_origem"
}

ORDENS = {
    "asc": "ASC",
    "desc": "DESC"
}

if __name__ == "__main__":
    app.run()