# Seed (datos de ejemplo)

Este proyecto incluye un comando para sembrar datos inmobiliarios de ejemplo.

Uso:

```bash
python manage.py seed --locations 5 --properties 20 --images 3
```

Esto creara ubicaciones y propiedades coherentes con el dominio: ciudades,
barrios, titulos, descripciones, precios, habitaciones, banos, area e imagenes.

Para generar siempre el mismo set durante pruebas o demos:

```bash
python manage.py seed --locations 5 --properties 20 --images 3 --seed 7
```
