"""
Quiz #4 - NoSQL (Base de datos de documentos con MongoDB)
Demostración: catálogo de una tienda en línea.

Ejecutar:
    python main.py              # usa MongoDB real (localhost:27017)
    USAR_MOCK=1 python main.py  # usa MongoDB simulada en memoria
"""
import json

from catalogo import Catalogo
from datos_iniciales import PRODUCTOS
from db import obtener_bd


def mostrar(titulo, datos):
    print(f"=== {titulo} ===")
    print(json.dumps(datos, indent=2, ensure_ascii=False, default=str))
    print()


def main():
    catalogo = Catalogo(obtener_bd())

    # 1. Cargar documentos con esquemas distintos
    catalogo.cargar_productos([dict(p) for p in PRODUCTOS])
    print(f"Se cargaron {len(PRODUCTOS)} productos.\n")

    # 2. Insertar un producto con campos totalmente nuevos (sin migraciones)
    catalogo.agregar_producto({
        "sku": "MOU-003",
        "nombre": "Mouse Logitech G203",
        "categoria": "electronica",
        "precio": 15000,
        "stock": 12,
        "especificaciones": {"dpi": 8000, "rgb": True},
        "garantia_meses": 24,  # campo que ningún otro producto tiene
        "etiquetas": ["gaming", "oferta"],
        "resenas": [],
    })
    mostrar("Producto nuevo (MOU-003)", catalogo.buscar_por_sku("MOU-003"))

    # 3. Consultas
    mostrar("Libros", catalogo.listar_por_categoria("libros"))

    mostrar(
        "Electrónica con 16 GB de RAM o más (consulta sobre un subdocumento)",
        catalogo.filtrar({"especificaciones.ram_gb": {"$gte": 16}}),
    )

    mostrar(
        "Productos para estudiantes con precio <= 50 000 (búsqueda en arreglo)",
        [{"sku": p["sku"], "nombre": p["nombre"], "precio": p["precio"]}
         for p in catalogo.filtrar({"etiquetas": "estudiantes", "precio": {"$lte": 50000}})],
    )

    mostrar(
        "Camisetas disponibles en talla XL",
        [p["nombre"] for p in catalogo.filtrar({"tallas": "XL"})],
    )

    # 4. Actualizaciones
    catalogo.actualizar_precio("AUD-002", 31000)
    print("Precio de AUD-002 actualizado a 31 000.")

    print("Vender 3 LAP-001:", "OK" if catalogo.vender("LAP-001", 3) else "sin stock")
    print("Vender 1 LIB-101:", "OK" if catalogo.vender("LIB-101", 1) else "sin stock")
    print()

    catalogo.agregar_resena("CAM-010", "jose", 5, "Excelente calidad")
    catalogo.agregar_resena("MOU-003", "dani", 4, "Buen mouse por el precio")
    mostrar("Reseñas de CAM-010 (embebidas en el documento)",
            catalogo.buscar_por_sku("CAM-010")["resenas"])

    # 5. Agregaciones
    mostrar("Resumen por categoría", catalogo.resumen_por_categoria())
    mostrar("Productos mejor calificados", catalogo.mejor_calificados())

    # 6. Eliminación
    catalogo.eliminar("LIB-101")
    print("LIB-101 eliminado. ¿Existe todavía?:", catalogo.buscar_por_sku("LIB-101") is not None)


if __name__ == "__main__":
    main()
