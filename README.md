# Ejemplo 01: de Django clásico a una API

Base de trabajo para retomar una aplicación Django renderizada en el servidor y, durante la clase, hacerla evolucionar hacia una API consumida desde React.

El repositorio comienza con dos aplicaciones independientes:

- `backend/`: Django, el modelo `Activity`, SQLite y una vista HTML clásica.
- `frontend/`: Vite + React + TypeScript para la implementación cliente del laboratorio.
- `frontend-astro/`: Astro con salida estática y una isla React para consultar y modificar inscripciones.

## Puesta en marcha local

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

### 2. Frontend

En otra terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

Abrir <http://127.0.0.1:5173/>.

### 3. Frontend Astro

En otra terminal, con el backend encendido:

```bash
cd frontend-astro
pnpm install
pnpm dev
```

Abrir <http://localhost:4321/>.

`frontend-astro` combina generación estática con interactividad selectiva:

- La portada, el listado y los detalles de actividades se generan como HTML durante el build.
- `src/pages/activities/[id].astro` usa `getStaticPaths()` para crear una ruta estática por actividad.
- `BaseLayout.astro` comparte la estructura HTML, navegación, metadatos y el indicador de modo mediante `Astro.props` y `<slot />`.
- `EnrollmentPanel.tsx` se incorpora como isla React con `client:load`; solo esta zona se hidrata en el navegador.
- La isla consulta el estado del participante y permite inscribirse o cancelar mediante la API.
- La identidad didáctica se valida como UUID, se guarda en `localStorage` y se envía mediante `X-Participant-ID`.
- El cliente tipado normaliza respuestas, errores de red, estados HTTP `400`, `404`, `409` y `500+`, además de la respuesta `204` de cancelación.
- La inscripción utiliza `PUT` de forma idempotente: `201` cuando se crea y `200` cuando ya existía.
- El proxy de Vite permite que el navegador use `/api/v1` sin modificar el backend ni depender de CORS.

Variables opcionales para `frontend-astro`:

| Variable                | Uso                                                                   |
| ----------------------- | --------------------------------------------------------------------- |
| `API_BUILD_URL`         | URL absoluta de la API usada por Node durante el build.               |
| `PUBLIC_API_URL`        | Base de API usada por la isla en el navegador; normalmente `/api/v1`. |
| `PUBLIC_PARTICIPANT_ID` | UUID precargado del participante de laboratorio.                      |

Comandos principales:

```bash
cd frontend-astro
pnpm astro check
pnpm build
pnpm preview
```

## Puesta en marcha con Docker Compose

Docker Compose queda preparado para uso futuro; no es necesario para seguir la primera clase.

```bash
docker compose up --build
```

El backend queda disponible en <http://127.0.0.1:8000/> y el frontend en <http://127.0.0.1:5173/>. El comando del backend aplica las migraciones y carga los datos de muestra antes de iniciar el servidor.

Para detener ambos servicios:

```bash
docker compose down
```

## Verificación rápida

```bash
cd backend
python manage.py test

cd ../frontend
pnpm build

cd ../frontend-astro
pnpm astro check
pnpm build
```

## API versionada (v1/v2)

El backend expone dos versiones del contrato HTTP que conviven bajo el mismo
proyecto. La rama `versionado` introdujo la v2 sin tocar la v1.

Reglas del versionado:

- `v1` queda **exactamente** como estaba: `capacity` y `available_slots` viajan
  en el nivel raíz de `Activity`.
- `v2` agrupa esos campos en `availability`:
  `{ "id": "...", "title": "...", "starts_at": "...", "availability": { "capacity": 20, "available_slots": 3 } }`.
- `Enrollment`, los errores (`code` + `message`) y la idempotencia son
  idénticos entre versiones.
- La lógica de dominio y la persistencia son compartidas: las v2 extienden las
  vistas v1 (`ActivityListViewV2(ActivityListView)`, ...) y solo cambian el
  serializador público (`serializer_class`) y los metadatos de OpenAPI.

Endpoints disponibles:

| Método   | Endpoint                            | Versión |
| -------- | ----------------------------------- | ------- |
| `GET`    | `/api/v1/activities/`               | v1      |
| `GET`    | `/api/v1/activities/{activity_id}/` | v1      |
| `GET`    | `/api/v1/me/enrollments/`           | v1      |
| `PUT`    | `/api/v1/me/enrollments/{id}/`      | v1      |
| `DELETE` | `/api/v1/me/enrollments/{id}/`      | v1      |
| `GET`    | `/api/v2/activities/`               | v2      |
| `GET`    | `/api/v2/activities/{activity_id}/` | v2      |
| `GET`    | `/api/v2/me/enrollments/`           | v2      |
| `PUT`    | `/api/v2/me/enrollments/{id}/`      | v2      |
| `DELETE` | `/api/v2/me/enrollments/{id}/`      | v2      |

La documentación OpenAPI también se genera por versión:

- `http://127.0.0.1:8000/api/v1/openapi.json` — solo el contrato v1.
- `http://127.0.0.1:8000/api/v2/openapi.json` — solo el contrato v2.
- `http://127.0.0.1:8000/api/openapi.json` — esquema combinado (v1 + v2).
- `http://127.0.0.1:8000/api/docs` — Swagger UI del esquema combinado.

La suite de tests cubre la regresión de v1, la coexistencia de ambas versiones
(idempotencia del `PUT`/`DELETE`, errores consistentes) y la diferencia
estructural de `Activity` en cada OpenAPI:

```bash
cd backend
python manage.py test
```

## Punto de partida didáctico

El proyecto conserva la vista HTML clásica y las implementaciones cliente como
etapas comparables. El backend Django expone la API JSON documentada en
`API.md`; `frontend/` permite trabajar con Vite + React y `frontend-astro/`
muestra la diferencia entre HTML generado en build e interactividad hidratada
por Astro. Para observar la arquitectura híbrida, desactivar JavaScript deja
visible el contenido estático de actividades, mientras la isla de inscripción
queda en su estado inicial.
