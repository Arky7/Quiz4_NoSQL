# Quiz #4 – NoSQL

Algoritmos y Estructuras de Datos II (CE 2103) – II Semestre 2026
Instituto Tecnológico de Costa Rica – Ingeniería en Computadores

**Integrantes:** _(Ricardo Bolaños Sanabria y Alejandro Arias López)_

**Tipo de base de datos elegido:** Documentos (MongoDB)
**Lenguaje:** Python

---

## El escenario

Para este quiz decidimos imaginar una tienda en línea pequeña que necesita guardar la información de los productos que vende. Lo interesante es que la tienda vende cosas muy diferentes entre sí: computadoras y audífonos, ropa y libros. Cada tipo de producto necesita datos distintos. Por ejemplo, a una laptop le interesa saber cuánta memoria RAM tiene y qué procesador usa, a una camiseta le interesa saber en qué tallas viene y a un libro le interesa saber quién lo escribió y en qué idioma está. Además, los clientes pueden dejar reseñas con una cantidad de estrellas y un comentario.

Si quisiéramos guardar todo esto en una base de datos con tablas, como las que se ven normalmente, nos encontraríamos con algunos problemas. Si usamos una sola tabla de productos, tendría muchísimas columnas y la mayoría quedarían vacías, porque un libro no tiene RAM y una camiseta no tiene autor. Si en cambio hacemos una tabla para cada tipo de producto, cada vez que la tienda quiera vender algo nuevo con datos diferentes habría que cambiar la estructura de la base de datos. Y para mostrar un producto con sus reseñas habría que juntar información de varias tablas distintas.

Por eso pensamos que una base de datos de documentos era una buena opción para este caso.

## Cómo usamos la base de datos de documentos

En una base de datos de documentos, en lugar de guardar la información en filas y columnas, cada cosa se guarda como un "documento", que se parece mucho a un objeto o a un diccionario de Python. Cada documento puede tener los campos que necesite, y dos documentos de la misma colección no tienen que tener la misma forma. Usamos MongoDB, que es una de las bases de datos de este tipo más conocidas, y Python porque los documentos se manejan prácticamente igual que los diccionarios, lo que hizo que el código fuera bastante sencillo.

En nuestro programa cada producto es un documento y todos se guardan juntos en una colección llamada `productos`. Así se ve, por ejemplo, la laptop:

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

Y así se ve un libro, que está guardado en la misma colección pero tiene otros campos:

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

Lo primero que notamos es que no tuvimos que definir columnas antes de guardar nada. Cada producto simplemente lleva los datos que le corresponden. Para probarlo, en el programa agregamos un mouse que tiene un campo que ningún otro producto tiene (los meses de garantía) y la base de datos lo aceptó sin tener que cambiar nada.

También aprovechamos que un documento puede tener otros datos adentro. Las especificaciones técnicas están agrupadas dentro del producto, y aun así se puede buscar por ellas; por ejemplo, el programa busca todas las computadoras con 16 GB de RAM o más. Lo mismo pasa con las listas: las tallas, los autores y las etiquetas se guardan como listas, y se puede preguntar algo como "¿qué productos vienen en talla XL?" o "¿qué productos tienen la etiqueta estudiantes?".

Las reseñas decidimos guardarlas dentro del mismo documento del producto. De esta forma, cuando se busca un producto, ya vienen sus reseñas incluidas y no hay que ir a buscarlas a otro lado. Como es una tienda pequeña y cada producto tiene pocas reseñas, nos pareció lo más práctico. Leímos que si un producto tuviera miles de reseñas sería mejor guardarlas aparte, porque los documentos en MongoDB tienen un tamaño máximo.

Con esto el programa puede hacer lo básico que haría cualquier tienda: agregar productos, buscarlos por código o por categoría, cambiar precios, agregar reseñas y eliminar productos. También tiene una función para vender que solo descuenta del inventario si hay suficientes unidades, para que nunca quede un número negativo. Por último, le pedimos a MongoDB que calcule dos pequeños reportes: cuántos productos y cuánto inventario hay en cada categoría junto con su precio promedio, y cuáles productos tienen mejor calificación según el promedio de estrellas de sus reseñas.

## Archivos del proyecto

- `main.py`: es el programa principal. Corre todo el ejemplo de principio a fin y muestra los resultados.
- `catalogo.py`: tiene todas las funciones que trabajan con la base de datos (agregar, buscar, actualizar, borrar y los reportes).
- `datos_iniciales.py`: los productos de ejemplo con los que arranca la tienda.
- `db.py`: se encarga de conectarse a MongoDB.
- `docker-compose.yml`: sirve para levantar MongoDB con Docker.
- `requirements.txt`: las librerías que hay que instalar.

## Cómo correrlo

Primero hay que instalar las librerías:

```bash
pip install -r requirements.txt
```

Si se tiene Docker, se puede levantar MongoDB y correr el programa así:

```bash
docker compose up -d
python main.py
```

Si no se quiere instalar MongoDB, el programa también puede usar una versión simulada que funciona en memoria (la librería `mongomock`). Solo hay que correrlo de esta forma:

```bash
# Linux / macOS
USAR_MOCK=1 python main.py

# Windows (PowerShell)
$env:USAR_MOCK="1"; python main.py
```

Al correrlo, el programa carga los productos, agrega el mouse nuevo, hace varias búsquedas, cambia un precio, intenta vender dos productos (uno con inventario y otro agotado), agrega reseñas, muestra los dos reportes y al final elimina un producto.

## Conclusión

Con este quiz entendimos mejor para qué sirve una base de datos de documentos. En este caso funcionó bien porque los productos de la tienda no tienen todos la misma forma y porque normalmente se consulta un producto completo a la vez, con sus datos y sus reseñas. MongoDB nos permitió guardar cada producto tal como lo usamos en el programa, sin tener que inventar tablas extra ni dejar columnas vacías, y aun así pudimos hacer búsquedas y reportes sin complicarnos mucho.

## Referencias

- Documentación de MongoDB: https://www.mongodb.com/docs/manual/
- Documentación de PyMongo: https://pymongo.readthedocs.io/
