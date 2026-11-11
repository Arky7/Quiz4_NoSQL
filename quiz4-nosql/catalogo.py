from datetime import datetime, timezone


class Catalogo:
    def __init__(self, bd):
        self.productos = bd["productos"]
        self.productos.create_index("sku", unique=True)
        self.productos.create_index("categoria")

    def agregar_producto(self, producto: dict):
        return self.productos.insert_one(producto).inserted_id

    def cargar_productos(self, lista: list):
        self.productos.delete_many({})
        self.productos.insert_many(lista)

    def buscar_por_sku(self, sku: str):
        return self.productos.find_one({"sku": sku}, {"_id": 0})

    def listar_por_categoria(self, categoria: str):
        return list(self.productos.find({"categoria": categoria}, {"_id": 0}))

    def filtrar(self, filtro: dict):
        return list(self.productos.find(filtro, {"_id": 0}).sort("precio", 1))

    def actualizar_precio(self, sku: str, nuevo_precio: float):
        return self.productos.update_one(
            {"sku": sku}, {"$set": {"precio": nuevo_precio}}
        ).modified_count

    def vender(self, sku: str, cantidad: int) -> bool:
        res = self.productos.update_one(
            {"sku": sku, "stock": {"$gte": cantidad}},
            {"$inc": {"stock": -cantidad}},
        )
        return res.modified_count == 1

    def agregar_resena(self, sku: str, usuario: str, estrellas: int, comentario: str):
        resena = {
            "usuario": usuario,
            "estrellas": estrellas,
            "comentario": comentario,
            "fecha": datetime.now(timezone.utc),
        }
        return self.productos.update_one(
            {"sku": sku}, {"$push": {"resenas": resena}}
        ).modified_count

    def eliminar(self, sku: str):
        return self.productos.delete_one({"sku": sku}).deleted_count

    def resumen_por_categoria(self):
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
