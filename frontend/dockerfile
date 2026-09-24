FROM node:24.20.0-slim

RUN corepack enable pnpm

WORKDIR /app

# El código de la app no se copia: se monta en runtime con -v sobre /app.

EXPOSE 5173

CMD ["pnpm", "dev"]
