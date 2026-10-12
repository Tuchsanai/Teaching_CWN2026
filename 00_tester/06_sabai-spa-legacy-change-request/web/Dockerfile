# syntax=docker/dockerfile:1.7
# สบายใจ สปา · web (Next.js standalone) · build ไม่ต่อฐานข้อมูล
# seed SQL มาจาก db/init/02-seed.sql ผ่าน additional_contexts "dbinit" (แหล่งเดียว ไม่มีสำเนาซ้ำ)

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund --ignore-scripts

FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npx next build

FROM node:22-alpine AS run
WORKDIR /app
RUN apk add --no-cache tzdata
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    TZ=Asia/Bangkok \
    SEED_SQL_PATH=/app/sql/02-seed.sql \
    PHOTO_DIR=/app/private/photos
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/private ./private
COPY --from=dbinit --chown=node:node 02-seed.sql ./sql/02-seed.sql
USER node
EXPOSE 3000
CMD ["node", "server.js"]
