---
name: ui-design
description: Diseña o modifica interfaces React con shadcn/ui, Tailwind y criterios de accesibilidad y responsive del proyecto.
---

# UI Design con shadcn/ui

Usa esta skill en tareas que creen o modifiquen pantallas, formularios, diálogos, tablas, navegación o estados visuales. No es necesaria para cambios sin UI, como servicios, lógica de negocio o utilidades.

## Preparación

Antes de implementar, verifica `frontend/components.json`, las dependencias y configuración de Tailwind, los aliases de TypeScript/Vite, `src/components/ui` y `src/lib/utils.ts`.

Si shadcn/ui no está configurado, inicialízalo para Vite con pnpm y configura Tailwind, aliases y el helper `cn` antes de crear UI. Mantén los componentes de shadcn en `src/components/ui` y sus imports bajo `@source`.

## Selección de componentes

Antes de agregar un primitive, revisa los componentes de `src/components/ui` y sus usos. Prefiere extender, componer o reutilizar una implementación existente. Incorpora solamente los componentes de shadcn que la tarea requiere; no instales el catálogo completo ni recrees manualmente componentes que el design system ya provee.

## Implementación

- Usa variantes, tokens y utilidades de Tailwind existentes; evita estilos inline y valores aislados cuando exista una alternativa del sistema.
- Mantén separadas la lógica de dominio y la presentación. Los componentes de una feature viven en su carpeta; los reutilizables, en `src/components/`.
- Incluye los estados relevantes: carga, vacío, error, disabled, foco y selección cuando correspondan.
- Usa HTML semántico, labels asociados, nombres accesibles para controles con iconos, foco visible y navegación por teclado. No dependas solo del color para comunicar estado.
- Diseña para móvil primero, sin overflow horizontal, y adapta grids, formularios y diálogos para tablet y escritorio.

## Validación

Confirma que se reutilizaron primitives existentes, que se agregaron solo las dependencias necesarias y que labels, teclado, foco y contraste básico funcionan. Revisa los breakpoints principales y ejecuta los controles de Definition of Done del repositorio.
