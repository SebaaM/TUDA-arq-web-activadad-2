# frontend-astro

Frontend del laboratorio TUDA construido con **Astro** (salida estática) y una
única **isla React** para la inscripción. Convive con `frontend/` (Vite) sin
modificarlo.

## Arquitectura en una frase

El listado y los detalles de actividades son **HTML generado durante el build**
(verde lima); el estado de inscripción se **consulta y modifica en el
navegador** desde una isla hidratada con `client:load` (cian).

```text
src/
├── components/EnrollmentPanel.tsx   # isla interactiva (client:load)
├── layouts/BaseLayout.astro         # header, nav, indicador de modo, footer
├── lib/api.ts                       # cliente tipado de la API
├── lib/format.ts                    # formateo compartido
├── pages/index.astro                # portada con evidencia arquitectónica
├── pages/activities/index.astro     # listado estático (build)
├── pages/activities/[id].astro      # detalle estático + isla
├── styles/global.css                # tema oscuro/neón, estados y accesibilidad
└── types/activity.ts                # contrato de la API (API.md)
```

## Requisitos

- Node 22.12+ y pnpm.
- El backend Django corriendo en `http://127.0.0.1:8000` con datos sembrados
  (`python manage.py seed_activities` / `seed_participants_and_enrollments`).

## Variables de entorno

Copiar `.env.example` a `.env`:

| Variable | Uso |
| --- | --- |
| `API_BUILD_URL` | URL absoluta que usa Node durante el build para consultar la API. |
| `PUBLIC_API_URL` | Base que usa la isla en el navegador. Es relativa (`/api/v1`): el proxy de Vite la redirige al backend porque la API no envía cabeceras CORS y no se puede modificar. Ver `astro.config.mjs`. |
| `PUBLIC_PARTICIPANT_ID` | Identidad de laboratorio precargada (header `X-Participant-ID`). Debe existir en la base: ver `GET /api/v1/participants/`. |

## Comandos

| Comando | Acción |
| --- | --- |
| `pnpm install` | Instala dependencias |
| `pnpm dev` | Dev server en `localhost:4321` |
| `pnpm build` | Genera `dist/` consultando la API (si la API está apagada, genera un estado vacío explicativo) |
| `pnpm preview` | Sirve `dist/`; también proxifica `/api` |
| `pnpm astro check` | Typecheck de `.astro` + `.tsx` |

## Evidencia de laboratorio

1. `pnpm build` con el backend encendido.
2. Abrir `dist/activities/index.html`: los títulos y cupos están dentro del HTML.
3. Abrir un detalle: la zona `STATIC CONTENT` ya contiene los datos; la isla
   muestra "esperando consulta del navegador" hasta que React hidrata.
4. Con DevTools: observar `GET /me/enrollments/` y el `PUT` al inscribirse.
5. Desactivar JavaScript: los datos base siguen visibles; sólo la isla queda
   congelada en su estado inicial.

## Identidad de prueba

La API no tiene login: la identidad viaja en el header `X-Participant-ID`.
La isla guarda el UUID en `localStorage`, permite cambiarlo y avisa que es un
atajo didáctico de laboratorio, no una sesión real.
