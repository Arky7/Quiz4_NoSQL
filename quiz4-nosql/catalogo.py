"""
Operaciones sobre la colección "productos".

Cada producto es un DOCUMENTO (un diccionario de Python que MongoDB guarda
como BSON/JSON). Los productos no comparten un esquema fijo: una laptop tiene
"ram_gb", una camiseta tiene "tallas", un libro tiene "autor". Además, cada
documento lleva sus reseñas EMBEBIDAS dentro de él, en una lista.
"""
from datetime import datetime, timezone


class Catalogo:
    def __init__(self, bd):
        self.productos = bd["productos"]
        # Índices para que las búsquedas frecuentes sean rápidas
        self.productos.create_index("sku", unique=True)
        self.productos.create_index("categoria")

    # ---------- CREATE ----------
    def agregar_producto(self, producto: dict):
        """Inserta un documento. No hace falta definir columnas antes."""
        return self.productos.insert_one(producto).inserted_id

    def cargar_productos(self, lista: list):
        self.productos.delete_many({})
        self.productos.insert_many(lista)

    # ---------- READ ----------
    def buscar_por_sku(self, sku: str):
        return self.productos.find_one({"sku": sku}, {"_id": 0})

    def listar_por_categoria(self, categoria: str):
        return list(self.productos.find({"categoria": categoria}, {"_id": 0}))

    def filtrar(self, filtro: dict):
        """Consulta libre usando el lenguaje de consultas de MongoDB."""
        return list(self.productos.find(filtro, {"_id": 0}).sort("precio", 1))

    # ---------- UPDATE ----------
    def actualizar_precio(self, sku: str, nuevo_precio: float):
        return self.productos.update_one(
            {"sku": sku}, {"$set": {"precio": nuevo_precio}}
        ).modified_count

    def vender(self, sku: str, cantidad: int) -> bool:
        """Resta stock solo si hay suficiente (operación atómica)."""
        res = self.productos.update_one(
            {"sku": sku, "stock": {"$gte": cantidad}},
            {"$inc": {"stock": -cantidad}},
        )
        return res.modified_count == 1

    def agregar_resena(self, sku: str, usuario: str, estrellas: int, comentario: str):
        """Agrega una reseña DENTRO del documento del producto ($push)."""
        resena = {
            "usuario": usuario,
            "estrellas": estrellas,
            "comentario": comentario,
            "fecha": datetime.now(timezone.utc),
        }
        return self.productos.update_one(
            {"sku": sku}, {"$push": {"resenas": resena}}
        ).modified_count

    # ---------- DELETE ----------
    def eliminar(self, sku: str):
        return self.productos.delete_one({"sku": sku}).deleted_count

    # ---------- AGREGACIONES ----------
    def resumen_por_categoria(self):
        """Cantidad de productos, stock total y precio promedio por categoría."""
        pipeline = [
            {"$group": {
                "_id": "$categoria",
                "productos": {"$sum": 1},
                "stock_total": {"$sum": "$stock"},
                "precio_promedio": {"$avg": "$precio"},
            }},
            {"$sort": {"_id": 1}},
        ]
        return list(self.productos.aggregate(pipeline))

    def mejor_calificados(self, minimo_resenas: int = 1):
        """Promedio de estrellas por producto, calculado desde las reseñas embebidas."""
        pipeline = [
            {"$unwind": "$resenas"},
            {"$group": {
                "_id": "$sku",
                "nombre": {"$first": "$nombre"},
                "promedio": {"$avg": "$resenas.estrellas"},
                "cantidad": {"$sum": 1},
            }},
            {"$match": {"cantidad": {"$gte": minimo_resenas}}},
            {"$sort": {"promedio": -1, "cantidad": -1}},
        ]
        return list(self.productos.aggregate(pipeline))
