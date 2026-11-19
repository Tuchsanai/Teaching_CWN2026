# One image for web (Next.js), dispatcher, migrate/seed and the test-profile mock-gateway.
FROM node:22-bookworm-slim

ENV NEXT_TELEMETRY_DISABLED=1 \
    PHOTOS_DIR=/data/photos \
    TZ=Asia/Bangkok

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build \
 && mkdir -p /data/photos \
 && chown -R node:node /data /app/.next

USER node
EXPOSE 3000
CMD ["npm", "start"]
