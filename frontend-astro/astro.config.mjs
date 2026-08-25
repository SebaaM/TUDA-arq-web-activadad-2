// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

/**
 * La API (Django Ninja) no envía cabeceras CORS y el backend no se puede
 * modificar. Por eso:
 *
 * - Durante el build (Node, sin CORS) se consulta la URL absoluta
 *   `API_BUILD_URL` (por defecto http://127.0.0.1:8000/api/v1).
 * - En el navegador la isla usa `PUBLIC_API_URL` (por defecto `/api/v1`,
 *   una ruta relativa) que este proxy redirige hacia la API local.
 */
const apiOrigin = process.env.API_ORIGIN ?? 'http://127.0.0.1:8000';
const apiProxy = {
  '/api': {
    target: apiOrigin,
    changeOrigin: true,
  },
};

export default defineConfig({
  integrations: [react()],
  vite: {
    server: {
      port: 4321,
      proxy: apiProxy,
    },
    preview: {
      proxy: apiProxy,
    },
  },
});
