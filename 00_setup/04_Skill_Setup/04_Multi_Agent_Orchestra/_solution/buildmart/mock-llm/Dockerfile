# mock-llm — build context = ROOT (docker-compose) · ไม่มี dependency
FROM node:22-alpine
WORKDIR /app
COPY mock-llm/package.json mock-llm/server.js mock-llm/selftest.mjs ./
ENV PORT=8000 NODE_ENV=production
EXPOSE 8000
USER node
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD wget -qO- http://127.0.0.1:8000/health >/dev/null || exit 1
CMD ["node", "server.js"]
