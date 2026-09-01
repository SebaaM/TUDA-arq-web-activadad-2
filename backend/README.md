# Backend Django y API OpenAPI

Aplicación Django con persistencia SQLite. La ruta `/` conserva la vista HTML clásica y `/api/v1` expone la API documentada con Django REST Framework y drf-spectacular.

## Requisitos

- Python 3.12 o posterior.

## Iniciar el proyecto

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

## Documentación Swagger

Con el servidor iniciado, abrir:

- Swagger UI: <http://127.0.0.1:8000/api/docs>
- Documento OpenAPI JSON: <http://127.0.0.1:8000/api/openapi.json>
- Alias del esquema: <http://127.0.0.1:8000/api/v1/openapi.json>

`seed_activities` se puede ejecutar más de una vez: restaura el mismo conjunto de actividades sin duplicarlas.

## Contrato HTTP

| Método | Ruta | Éxito |
| --- | --- | --- |
| `GET` | `/api/v1/activities/` | `200`, colección con cupos disponibles |
| `GET` | `/api/v1/activities/{activity_id}/` | `200`, actividad |
| `GET` | `/api/v1/participants/` | `200`, participantes |
| `GET` | `/api/v1/participants/{participant_id}/` | `200`, participante |
| `GET` | `/api/v1/me/enrollments/` | `200`, inscripciones propias |
| `PUT` | `/api/v1/me/enrollments/{activity_id}/` | `201` al crear o `200` si ya existía (idempotente) |
| `DELETE` | `/api/v1/me/enrollments/{activity_id}/` | `204`, sin body (idempotente) |

Las operaciones bajo `/me` requieren `X-Participant-ID`. Una identidad ausente o desconocida produce `401`; una actividad o participante inexistente, `404`; y una actividad sin cupos, `409`. Los métodos no habilitados producen `405` con encabezado `Allow`.

### Formato de representación pública

Una actividad (tanto en la colección como en el detalle):

```json
{
  "id": "uuid",
  "title": "Taller de HTTP",
  "starts_at": "2026-04-10T18:00:00-03:00",
  "capacity": 20,
  "available_slots": 3
}
```

Una inscripción:

```json
{
  "activity_id": "uuid",
  "enrolled_at": "2026-04-03T15:20:00-03:00"
}
```

### Formato de error estable

Todos los errores usan una forma estable con `code` y `message`:

```json
{
  "code": "capacity_exhausted",
  "message": "No hay lugares disponibles."
}
```

Códigos disponibles: `capacity_exhausted`, `activity_not_found`, `authentication_required`.

### Idempotencia

- Un mismo `PUT` repetido devuelve `200` con la inscripción ya existente (se conserva `enrolled_at`, no se crea otra fila) en lugar de `409`.
- Un mismo `DELETE` repetido devuelve `204` igualmente; el efecto final es "sin inscripción".

## Comandos útiles

```bash
# Ejecutar las pruebas
python manage.py test

# Abrir la consola de Django
python manage.py shell

# Vaciar la base y volver a cargar los datos de muestra
python manage.py flush --noinput
python manage.py seed_activities
```

## Estructura relevante

- `activities/models.py`: modelos `Activity`, `Participant` y `Enrollment`.
- `activities/views.py`: vista HTML clásica y vistas DRF de la API.
- `activities/api_urls.py`: enrutamiento de la API.
- `activities/serializers.py`: representaciones JSON públicas.
- `activities/templates/activities/activity_list.html`: documento HTML producido por Django.
- `activities/management/commands/seed_activities.py`: datos reproducibles.

SQLite usa el archivo `db.sqlite3`, creado por `python manage.py migrate` y excluido de Git.
