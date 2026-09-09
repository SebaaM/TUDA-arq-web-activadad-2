# Contexto para agentes — TUDA Arquitectura Web 2026 · Ejemplo 01

## Rol de este archivo

Este documento es el punto de partida para cualquier agente que trabaje en el
repositorio. Describe el estado efectivo del código, las decisiones
arquitectónicas y los límites que se deben respetar. Para instalación, comandos
de uso y documentación de usuario, consultar `README.md`; no duplicarlos aquí.

## Objetivo del proyecto

Proyecto didáctico para comparar una aplicación Django tradicional con una API
REST y un frontend híbrido. El dominio es actividades, participantes e
inscripciones.

- `backend/`: Django 5, Django REST Framework y SQLite. Conserva `GET /` como
  vista HTML clásica y publica una API REST versionada.
- `frontend-astro/`: Astro 7 + React 19. Genera el contenido de actividades en
  build y conserva la inscripción como una isla React interactiva.

## Estado y límites actuales

- **No se realizaron cambios en la base de datos**: no alterar modelos,
  migraciones, `backend/db.sqlite3`, comandos de seed ni datos existentes salvo
  que una tarea lo pida de forma explícita.
- **No se realizaron cambios en Docker**: no modificar `compose.yaml`,
  `backend/Dockerfile` ni el flujo de contenedores salvo solicitud explícita.
- El directorio `frontend/` no existe, aunque `README.md` y `compose.yaml` lo
  mencionan. La interfaz vigente está únicamente en `frontend-astro/`.
- `README.md`, `API.md` y `RESUMEN_CONTEXTO.md` contienen material de etapas
  anteriores. Antes de cambiar contratos, priorizar rutas, vistas,
  serializadores y pruebas del backend como fuente de verdad.

## Backend: contrato vigente

Los modelos son `Activity`, `Participant` y `Enrollment`. `Enrollment` tiene
una restricción única por actividad y participante. La disponibilidad se
calcula en tiempo de consulta, no se persiste.

La lógica de dominio está en `backend/activities/services.py` y debe seguir
centralizada allí:

- `PUT` de inscripción es idempotente: `201` al crear, `200` si ya existía.
- `DELETE` de inscripción es idempotente: siempre deja al participante sin
  inscripción y responde `204`.
- La capacidad agotada responde `409` con `capacity_exhausted`.

Las rutas v1 y v2 coexisten. Mantener **v1 sin cambios incompatibles**.

- Ambas exponen actividades e inscripciones bajo `/api/v1/` y `/api/v2/`.
- Sólo v1 expone participantes.
- La diferencia entre las versiones es la representación de actividad:
  - v1: `capacity` y `available_slots` en la raíz.
  - v2: ambos campos dentro de `availability`.
- Las operaciones `/me` requieren el header `X-Participant-ID` de un
  participante existente. Una identidad inválida o ausente devuelve `401` con
  `authentication_required`.
- Las respuestas exitosas son recursos JSON directos, no usan un envoltorio
  `{data, error}`. La baja correcta no tiene cuerpo (`204`).

Al tocar un endpoint, mantener alineados vista, serializador, anotaciones
`drf-spectacular`, rutas y pruebas. Las especificaciones OpenAPI por versión
se generan en `/api/v1/openapi.json` y `/api/v2/openapi.json`.

## Trazabilidad

`CorrelationMiddleware` asigna o conserva `X-Correlation-ID` y lo devuelve
en cada respuesta. Los eventos de negocio se escriben como JSON en consola y
en `backend/logs/trace.log`.

No registrar payloads, cookies, tokens ni credenciales. Conservar los eventos
existentes y el mismo identificador de correlación a lo largo de cada request.

## Frontend Astro

- El listado y los detalles usan `GET /api/v1/activities/` durante el build;
  deben seguir funcionando como HTML estático sin JavaScript.
- `src/components/EnrollmentPanel.tsx` es la única isla React y se hidrata con
  `client:load`. Su estado usa `localStorage` y el header
  `X-Participant-ID`; no hay login real.
- `src/lib/api.ts` resuelve la API absoluta durante build y una ruta relativa
  (`/api/v1`) en el navegador mediante el proxy de Vite.
- Si el backend está caído durante el build, el sitio genera un estado vacío
  explicativo; no hacer que el build falle por esa condición sin una decisión
  explícita.

## Inconsistencias que deben conocerse antes de modificar

El frontend Astro aún refleja parte de un contrato anterior:

- `src/lib/api.ts` intenta leer errores del campo `error`, mientras el backend
  actual usa `{code, message}`.
- Clasifica `400`, pero el backend usa `401` para identidad inválida.
- Solicita `DELETE /me/enrollments/{id}/cancel/`, pero el backend actual
  implementa `DELETE /me/enrollments/{id}/`.
- El comentario de `astro.config.mjs` menciona Django Ninja, pero el backend
  usa Django REST Framework.

No corregir estas discrepancias de forma incidental: si una tarea afecta el
contrato o la isla, resolverlas de manera coherente y actualizar la
documentación correspondiente en el mismo cambio.

## Criterios para cambios futuros

- Preservar la separación didáctica entre contenido de build y estado de
  navegador.
- Preservar v1; introducir una versión nueva ante cambios incompatibles.
- Mantener contratos, frontend y documentación sincronizados cuando el alcance
  incluya una modificación de API.
- Evitar cambios no solicitados en base de datos y Docker.
