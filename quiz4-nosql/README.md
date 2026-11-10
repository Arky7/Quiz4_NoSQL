# Quiz #4 – NoSQL: Base de datos de documentos (MongoDB)

**Curso:** Algoritmos y Estructuras de Datos II (CE 2103) – II Semestre 2026
**Instituto Tecnológico de Costa Rica – Ingeniería en Computadores**

**Tipo de base de datos NoSQL elegido:** Documentos
**Motor:** MongoDB
**Lenguaje:** Python 3 (con el driver oficial `pymongo`)

---

## 1. Escenario (contexto del problema)

Una pequeña **tienda en línea** necesita guardar su **catálogo de productos**. La tienda vende cosas muy distintas entre sí:

| Categoría   | Datos que necesita cada producto                          |
|-------------|-----------------------------------------------------------|
| Electrónica | RAM, almacenamiento, procesador, batería, DPI, garantía…  |
| Ropa        | tallas disponibles, material                              |
| Libros      | autores, edición, idioma                                  |

Además, los clientes pueden dejar **reseñas** (usuario, estrellas, comentario y fecha) sobre cada producto.

En una base de datos **relacional** esto genera problemas:

- Una sola tabla `productos` tendría decenas de columnas, casi todas en `NULL` (un libro no tiene "RAM", una camiseta no tiene "autor").
- Otra opción es una tabla por categoría, o el patrón EAV (entidad-atributo-valor), pero cada producto nuevo con un atributo diferente obliga a hacer `ALTER TABLE` o migraciones.
- Las reseñas y las listas (tallas, autores, etiquetas) necesitan tablas aparte y varios `JOIN` para mostrar un solo producto.

El catálogo cambia seguido y casi siempre se consulta **un producto completo a la vez** (la página del producto). Por eso encaja bien en una **base de datos orientada a documentos**.

## 2. Cómo se usó la base de datos de documentos

### Modelo de datos

Cada producto es **un documento** dentro de la colección `productos` de la base `tienda_online`. Un documento es un objeto tipo JSON (MongoDB lo guarda como BSON) que puede contener subdocumentos y arreglos. En Python se maneja como un diccionario normal.

Ejemplo de documento:

```json
{
  "sku": "LAP-001",
  "nombre": "Laptop Lenovo IdeaPad 5",
  "categoria": "electronica",
  "precio": 650000,
  "stock": 8,
  "especificaciones": { "ram_gb": 16, "almacenamiento_gb": 512, "procesador": "Ryzen 7" },
  "etiquetas": ["laptop", "estudiantes", "oferta"],
  "resenas": [
    { "usuario": "ana",  "estrellas": 5, "comentario": "Muy rápida" },
    { "usuario": "luis", "estrellas": 4, "comentario": "Buena batería" }
  ]
}
```

Y un libro de la **misma colección** tiene campos completamente diferentes:

```json
{
  "sku": "LIB-100",
  "nombre": "Introduction to Algorithms",
  "categoria": "libros",
  "precio": 42000,
  "stock": 5,
  "autor": ["Cormen", "Leiserson", "Rivest", "Stein"],
  "edicion": 4,
  "idioma": "inglés",
  "resenas": [ ... ]
}
```

### Decisiones de diseño

| Característica de las BD de documentos | Cómo se aprovecha en el programa |
|---|---|
| **Esquema flexible** | Cada categoría guarda solo sus campos. En el programa se inserta un mouse con un campo nuevo (`garantia_meses`) sin modificar nada de la base. |
| **Subdocumentos** | Las especificaciones técnicas van en `especificaciones: {...}` y se consultan con notación de punto: `{"especificaciones.ram_gb": {"$gte": 16}}`. |
| **Arreglos** | `tallas`, `autor`, `colores` y `etiquetas` son listas. Buscar `{"tallas": "XL"}` encuentra los documentos cuyo arreglo contiene ese valor. |
| **Datos embebidos** | Las reseñas se guardan **dentro** del producto. Con una sola lectura se obtiene el producto y sus reseñas, sin `JOIN`. Para agregar una se usa `$push`. |
| **Operaciones atómicas por documento** | `vender()` usa `update_one` con el filtro `stock >= cantidad` y `$inc`, así nunca queda stock negativo aunque dos ventas ocurran al mismo tiempo. |
| **Índices** | Índice único sobre `sku` (no se repiten productos) e índice sobre `categoria` para listar rápido. |
| **Pipeline de agregación** | Se calculan reportes dentro de la base: resumen por categoría (`$group`) y ranking de productos por promedio de estrellas (`$unwind` sobre las reseñas embebidas + `$group` + `$sort`). |

> **¿Por qué embeber las reseñas y no ponerlas en otra colección?** Porque siempre se muestran junto al producto y una tienda pequeña tiene pocas por producto. Si un producto llegara a tener miles de reseñas, lo correcto sería moverlas a su propia colección para no acercarse al límite de 16 MB por documento.

### Operaciones implementadas (`catalogo.py`)

| Tipo | Método | Operación de MongoDB |
|---|---|---|
| Create | `agregar_producto`, `cargar_productos` | `insert_one`, `insert_many` |
| Read | `buscar_por_sku`, `listar_por_categoria`, `filtrar` | `find_one`, `find` |
| Update | `actualizar_precio` | `update_one` + `$set` |
| Update | `vender` | `update_one` + `$inc` con condición |
| Update | `agregar_resena` | `update_one` + `$push` |
| Delete | `eliminar` | `delete_one` |
| Reporte | `resumen_por_categoria` | `aggregate` con `$group` |
| Reporte | `mejor_calificados` | `aggregate` con `$unwind`, `$group`, `$match`, `$sort` |

## 3. Estructura del repositorio

```
.
├── main.py              # Programa de demostración (ejecuta todo el escenario)
├── catalogo.py          # Clase Catalogo: CRUD, consultas y agregaciones
├── datos_iniciales.py   # Productos de ejemplo con esquemas distintos
├── db.py                # Conexión a MongoDB (real o simulada)
├── docker-compose.yml   # Levanta un servidor MongoDB local
├── requirements.txt
└── README.md
```

## 4. Cómo ejecutarlo

### Requisitos

- Python 3.9 o superior
- Docker (opcional, para tener un MongoDB real)

```bash
pip install -r requirements.txt
```

### Opción A: con MongoDB real (recomendada)

```bash
docker compose up -d   # levanta MongoDB en localhost:27017
python main.py
```

Para usar otro servidor (por ejemplo, MongoDB Atlas):

```bash
MONGO_URI="mongodb+srv://usuario:clave@cluster.mongodb.net" python main.py
```

Luego puede inspeccionar los datos con **MongoDB Compass** conectándose a `mongodb://localhost:27017`, base `tienda_online`, colección `productos`.

### Opción B: sin instalar MongoDB

El programa puede usar `mongomock`, una MongoDB simulada en memoria con la misma API:

```bash
# Linux / macOS
USAR_MOCK=1 python main.py

# Windows (PowerShell)
$env:USAR_MOCK="1"; python main.py
```

## 5. Qué muestra la ejecución

1. Carga 5 productos de 3 categorías con estructuras diferentes.
2. Inserta un producto con un campo que nadie más tiene (esquema flexible).
3. Consultas: por categoría, por campo de un subdocumento (RAM ≥ 16 GB), por elemento de un arreglo (etiqueta "estudiantes", talla "XL") y por rango de precio.
4. Actualiza un precio, intenta dos ventas (una con stock y otra sin stock) y agrega reseñas embebidas.
5. Reportes con el pipeline de agregación: resumen por categoría y ranking por calificación.
6. Elimina un producto.

Fragmento de la salida:

```
Vender 3 LAP-001: OK
Vender 1 LIB-101: sin stock

=== Productos mejor calificados ===
[
  { "nombre": "Introduction to Algorithms", "promedio": 5.0, "cantidad": 2, "_id": "LIB-100" },
  { "nombre": "Laptop Lenovo IdeaPad 5",    "promedio": 4.5, "cantidad": 2, "_id": "LAP-001" },
  ...
]
```

## 6. Conclusión

Una base de datos de documentos fue adecuada para este escenario porque los productos tienen **estructuras heterogéneas** que cambian con el tiempo y porque la aplicación lee **cada producto como una unidad completa** (con sus especificaciones y reseñas). MongoDB permitió guardar cada producto tal como lo usa el programa, sin tablas extra, sin columnas vacías y sin `JOIN`, mientras que los índices, las consultas sobre subdocumentos y arreglos, y el pipeline de agregación cubren las búsquedas y reportes que necesita la tienda.

## Referencias

- Documentación de MongoDB: https://www.mongodb.com/docs/manual/
- Modelado de datos en MongoDB (embeber vs. referenciar): https://www.mongodb.com/docs/manual/data-modeling/
- Driver PyMongo: https://pymongo.readthedocs.io/
