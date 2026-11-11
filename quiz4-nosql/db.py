import os

NOMBRE_BD = "tienda_online"


def obtener_bd():
    if os.getenv("USAR_MOCK") == "1":
        import mongomock
        cliente = mongomock.MongoClient()
        print("[i] Usando MongoDB simulada en memoria (mongomock)\n")
    else:
        from pymongo import MongoClient
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        cliente = MongoClient(uri, serverSelectionTimeoutMS=3000)
        cliente.admin.command("ping")  # falla rápido si el servidor no está
        print(f"[i] Conectado a MongoDB en {uri}\n")
    return cliente[NOMBRE_BD]
