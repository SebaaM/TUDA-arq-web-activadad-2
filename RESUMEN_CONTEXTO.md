# Resumen del contexto de la conversación

## Fecha

19 de agosto de 2026.

## Proyecto

Repositorio ubicado en:

`TUDA-arq-web-2026-ejemplo-01`

El proyecto está organizado en dos partes principales:

- `backend/`: aplicación Django con SQLite.
- `frontend/`: aplicación frontend basada en React, TypeScript y Vite.

También incluye:

- `compose.yaml` para la orquestación con Docker Compose.
- `README.md` en la raíz.
- Documentación de la API en `backend/config/documentation.py` y plantillas relacionadas.

## Estado actual observado

### Backend

- Proyecto Django con `manage.py`.
- Base de datos SQLite en `backend/db.sqlite3`.
- Aplicación `activities` con modelos, vistas, URLs, representaciones, administración, migraciones y comandos de carga inicial.
- Plantilla para listar actividades en `backend/activities/templates/activities/activity_list.html`.
- Documentación API en formato OpenAPI, Jinja2, Swagger UI y ReDoc bajo `backend/jinja2/api_documentation/`.
- La documentación se define en `backend/config/documentation.py`.
- Las rutas públicas de documentación están en `backend/config/urls.py`.
- La API usa vistas Django nativas y `JsonResponse`, no vistas de Django REST Framework.

### Frontend

- Proyecto React con TypeScript.
- Configuración de Vite, ESLint, TypeScript y pnpm.
- Archivos principales: `src/App.tsx`, `src/App.css`, `src/index.css` y `src/main.tsx`.

## Archivos relevantes

- `backend/requirements.txt`
- `backend/config/settings.py`
- `backend/config/urls.py`
- `backend/config/documentation.py`
- `backend/jinja2/api_documentation/index.html`
- `backend/jinja2/api_documentation/swagger.html`
- `backend/jinja2/api_documentation/redoc.html`
- `backend/activities/urls.py`

## Acciones realizadas

- Se revisó la estructura del backend, las vistas de `activities` y sus rutas.
- Se añadieron a `backend/requirements.txt`:
  - `djangorestframework==3.16.1`
  - `drf-yasg==1.21.11`
  - `Jinja2==3.1.6`
- Se configuró Jinja2 como segundo motor de plantillas en `backend/config/settings.py`.
- Se creó una página Jinja2 en `/api-docs/` con enlaces a la documentación.
- Se crearon páginas Jinja2 para `/swagger/` y `/redoc/`.
- Se creó `/swagger.json` con un esquema OpenAPI explícito, porque `drf-yasg` no detectaba las vistas Django nativas y generaba `paths: {}`.
- El esquema documenta 8 rutas de la API, actividades, participantes e inscripciones.
- Se corrigió un `DELETE` duplicado en la documentación OpenAPI:
  - `/api/v1/me/enrollments/{activity_id}/` conserva solamente `PUT`.
  - `/api/v1/me/enrollments/{activity_id}/cancel/` conserva `DELETE`.
- Se actualizó `backend/README.md` con las URLs de documentación.

## URLs disponibles

- Página índice Jinja2: `http://127.0.0.1:8000/api-docs/`
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- Documento OpenAPI JSON: `http://127.0.0.1:8000/swagger.json`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## Validaciones realizadas

- `python manage.py check` finaliza sin errores.
- Jinja2 responde con HTTP 200 en `/api-docs/`.
- Swagger UI responde con HTTP 200 en `/swagger/`.
- OpenAPI responde con HTTP 200 en `/swagger.json`.
- El esquema contiene 8 rutas y solamente una operación `DELETE`.
- Se ejecutó el servidor de desarrollo en `127.0.0.1:8000`; el proceso terminó posteriormente al cerrarse el terminal.

## Problema observado al probar la API

- Las peticiones `PUT` y `DELETE` desde Swagger devolvieron HTTP 403 por falta de token CSRF.
- El middleware `django.middleware.csrf.CsrfViewMiddleware` está activo.
- Las vistas de escritura (`PUT` y `DELETE`) no están exentas de CSRF.
- Las peticiones de lectura (`GET`) respondieron correctamente.
- Este problema queda pendiente de decidir según el cliente previsto: enviar un token CSRF desde el cliente o aplicar una estrategia de autenticación/API adecuada para endpoints sin sesión.

## Alcance

- No se hicieron cambios en el frontend.
- No se ejecutaron builds del frontend ni despliegues.
- No se corrigió todavía el bloqueo CSRF de las operaciones `PUT` y `DELETE`.
