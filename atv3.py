from pymongo import MongoClient
from datetime import datetime, timedelta
import random

cliente = MongoClient("mongodb://localhost:27017/")

banco = cliente["seguranca"]
eventos = banco["eventos"]

eventos.delete_many({})

#coloquei isso pq tava mó ruim de testar, pq tava dando erro de duplicidade.
if "ttl_7_dias" in eventos.index_information():
    eventos.drop_index("ttl_7_dias")

eventos.create_index(
    "timestamp",
    expireAfterSeconds=604800, # 7 dias em segundos
    name="ttl_7_dias"
)

agora = datetime.now()
documentos = []

for i in range(200):
    segundos_atras = random.randint(0, 86400)

    evento = {
        "timestamp": agora - timedelta(seconds=segundos_atras),
        "tipo": "FAIL",
        "fonte": "auth",
        "ip": f"192.168.1.{random.randint(1, 254)}"
    }

    documentos.append(evento)

eventos.insert_many(documentos)

print(f"Eventos inseridos: {eventos.count_documents({})}")

inicio_janela = datetime.now() - timedelta(hours=24)

pipeline = [
    {
        "$match": {
            "tipo": "FAIL",
            "timestamp": {"$gte": inicio_janela}
        }
    },
    {
        "$group": {
            "_id": {"$hour": "$timestamp"},
            "total": {"$sum": 1}
        }
    },
    {
        "$sort": {"_id": 1}
    }
]

resultado = list(eventos.aggregate(pipeline))

print("\n=== Falhas por hora (últimas 24h) ===")

for item in resultado:
    hora = item["_id"]
    total = item["total"]
    barra = "█" * total

    print(f"{hora:02d}h | {barra} {total}")

if resultado:
    pico = max(resultado, key=lambda item: item["total"])

    print(
        f"\nHora de pico: {pico['_id']:02d}h "
        f"({pico['total']} falhas)"
    )

print(
    "Índice TTL ativo: eventos com mais de 7 dias "
    "serão removidos automaticamente."
)

# O TTL reduz a exposição de dados antigos e limita o impacto de acessos indevidos ou vazamentos.

cliente.close()