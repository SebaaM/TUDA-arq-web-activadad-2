# Guía del proyecto

## Stack

- La aplicación principal está en `frontend/` y utiliza React, TypeScript y Vite.
- El gestor de paquetes oficial es **pnpm**. Usar `pnpm` para instalar dependencias y ejecutar scripts; no usar npm ni yarn.
- `frontend-astro/` contiene la variante basada en Astro y `backend/` el servicio de API. Trabajar en `frontend/` salvo que una tarea requiera explícitamente modificar otro directorio.

## Estructura

- `frontend/src/main.tsx`: punto de entrada que monta la aplicación React.
- `frontend/src/App.tsx`: composición de la interfaz raíz.
- `frontend/src/components/ui/`: componentes generados y mantenidos mediante shadcn/ui.
- `frontend/src/components/`: componentes compartidos de la aplicación que no pertenecen a una feature.
- `frontend/src/features/<feature>/index.tsx`: entrada de cada funcionalidad; la UI, tipos, servicios y componentes propios viven dentro de su feature.
- `frontend/src/lib/`: utilidades compartidas, incluido `cn`.
- `frontend/public/`: archivos servidos directamente por Vite.
- `backend/`: API del proyecto.
- `.agents/skills/`: skills locales y reutilizables del repositorio.

## Convenciones

- Usar TypeScript y componentes funcionales de React. Nombrar componentes y sus archivos en `PascalCase`; hooks y utilidades en `camelCase`.
- Preferir `named exports`; no usar `export default` en componentes nuevos.
- Usar importaciones absolutas mediante `@source`.
- Toda feature nueva debe vivir en `src/features/<feature>/` y exponer `index.tsx`.
- Para tareas visuales o de interfaz, leer y aplicar `.agents/skills/ui-design/SKILL.md`.
- shadcn/ui es el design system obligatorio. Reutilizar primero `src/components/ui/` y agregar únicamente los componentes de shadcn necesarios; no recrear manualmente sus primitives.
- Usar Tailwind CSS, las variantes y tokens del design system. Respetar accesibilidad, responsive y consistencia visual.
- Mantener los componentes pequeños, con una responsabilidad clara, y actualizar la documentación afectada.
- Usar Conventional Commits al crear commits y comunicar los cambios de forma concisa.

## Definition of Done

Antes de finalizar cualquier modificación:

1. Verificar alcance, estados de error y ausencia de regresiones visibles.
2. Desde `frontend/`, ejecutar `pnpm format`, `pnpm lint` y `pnpm build`.
3. Si se modifica el backend, ejecutar su suite de pruebas y actualizar el contrato o la documentación de API correspondiente.
4. Revisar accesibilidad y comportamiento responsive en las tareas de interfaz.
5. Corregir los errores detectados; tras 10 intentos sin resolverlos, detenerse e informar el bloqueo y el error concreto.
6. Revisar el diff final y actualizar la documentación afectada.
