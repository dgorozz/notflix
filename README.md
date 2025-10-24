# NOTFLIX

Esta es una API desarrollada para el Módulo 02 del Máster en IA, Cloud Computing y DevOps de Pontia por Daniel Gómez Rodríguez.

## Database

La API utiliza una base de datos SQLite. Dispone de dos tablas 'shows' y 'sessions' que corresponden a series y sesiones de visualización. Intenta imitar el "seguir viendo ..." de Netflix.

### Tablas

_**shows**_:

- id (PK)
- name (string) -> nombre de la serie (único, no nullable)
- descripción (string) -> breve descripción/sinopsis de la serie
- gender (string) -> género(s) de la serie
- episodes (json) -> lista de enteros que define el número de episodios por temporada

_**sessions**_:

- id (PK)
- show_id (int) -> FK con el id de la serie a la que hace referencia
- season (int) -> temporada por la que va (por defecto se inicia a 1)
- episode (int) -> episodio por el que va (por defecto se inicia a 1)
- state (enum) -> estado de la serie: 'watching' (valor por defecto) o 'finished'
- start_date (datetime) -> fecha de inicio de la sesión
- end_date (datetime) -> fecha de finalización de la sesión (nulo por defecto)

## Usage

Para lanzar la API ejecutar el siguiente comando:

```shell
uvicorn api.main:app
```

Esto lanzará la API en el puerto 8000 (valor por defecto). En algunas ocasiones, es necesario poner el prefijo `python -m` antes del comando.

Para llenar la base de datos de información relevante hay que ejecutar el script `create_show_catalog.py` que llenará la tabla Shows con datos obtenidos de source.json que fueron generados con ChatGPT (no son datos fiables, únicamente orientativos).

El script para comprobar el funcionamiento de la API es cli.py, donde he usado la librería cmd built-in de Python para crear una interfaz interactiva en terminal.

```python
python cli.py
```

Se iniciará el siguiente mensaje y prompt:

```shell
🎬 Welcome to Notflix CLI. Write 'help' or '?' to see available commands.

notflix>
```

sobre el que ejecutar una serie de comandos.

### show command

```shell
show list               -> get show list
show <show_id> info     -> get show info
show <show_id> start    -> start show
```

- `show list` lanza una petición GET `/shows` para obtener todas las series almacenadas en la tabla 'shows'.
- `show <show_id> info` lanza una petición GET a `/shows/{show_id}` con `show_id` como path param para obtener la serie con ese id específico.
- `show <show_id> start` lanza una petición POST a `/shows/{show_id}/start` con `show_id` como path param para comenzar una sesión con ese show específico.
  - Lanza error 409 si se intenta comenzar una sesión sobre una serie con una sesión ya iniciada (sea cual sea su estado).

### session command

```shell
session list <finished|watching?>   -> list all session with optional filter
session <session_id> info           -> session info
session <session_id> delete         -> delete session
session <session_id> next           -> next episode
session <session_id> previous       -> previous episode
session <session_id> restart        -> restart show
session <session_id> goto <season> <episode> -> go to specific episode
```

- `session list` lanza una petición GET `/sessions` para obtener todas las sesiones almacenadas en la tabla 'session'. Permite un query param (`state`) par abuscar por estado (`watching` o `finished`). Por defecto busca todas las sesiones.
- `session <session_id> info` lanza una petición GET a `/sessions/{session_id}` con `session_id` como path param para obtener la sesión con ese id específico.
- `session <session_id> delete` lanza una petición DELETE a `/sessions/{session_id}` con `session_id` como path param para eliminar una sesión.
- `session <session_id> next` lanza una petición POST a `/sessions/{session_id}/next` con `session_id` como path param para avanzar un episodio en esa sesión. Si la sesión ya estaba en el último episodio, marcará la serie como 'finished'.
- `session <session_id> previous` lanza una petición POST a `/sessions/{session_id}/previous` con `session_id` como path param para retroceder un episodio en esa sesión.
  - Lanza error 400 si la serie ya se encontraba en el primer episodio
- `session <session_id> restart` lanza una petición POST a `/sessions/{session_id}/restart` con `session_id` como path param para reiniciar una sesión. Reiniciar implica devolver su estado a 'watching' y su temporada y episodio actual a 1.
- `session <session_id> goto <season> <episode>` lanza una petición POST a `/sessions/{session_id}/goto` con `session_id` como path param y un json con los campos `season` y `episode` introducidos para avanzar a un episodio específico.
  - Lanza error 404 si la temporada o el episodio no existen.

**Peculiaridades**

- En todos los casos que implique buscar por id, si la session/show no se encuntra, lanza un error 404.
- En los casos que implique navegación entre episodios (next, previous, goto), si la sesión está con `state=finished`, lanza error 400.

## Testing

En la ruta /tests hay una serie de tests desarrollados con la lógica de pytest (assertions) para comprobar el correcto funcionamiento de la API en todas las casuísticas y situaciones posibles.

Para ejecutarlos:

```shell
pytest -v
```

Usa TestClient de FastAPI y utiliza unos fixtures para servirse de una base de datos SQLite en memoria (efímera) y no crear conflicto sobre la base de datos original.
