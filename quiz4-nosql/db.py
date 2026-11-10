"""
Conexión a la base de datos MongoDB.

Por defecto se conecta a mongodb://localhost:27017 (por ejemplo, el contenedor
de docker-compose.yml). Se puede cambiar con la variable de entorno MONGO_URI.

Si se ejecuta con la variable USAR_MOCK=1, se usa mongomock: una MongoDB
simulada en memoria, útil para probar el programa sin instalar MongoDB.
"""
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
