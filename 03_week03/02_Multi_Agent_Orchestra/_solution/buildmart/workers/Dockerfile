# workers (chat / rag / notify / stt) — build context = ROOT · command เลือกใน docker-compose.yml
# โครง: /app/workers (โค้ด) + /app/shared (ROOT/shared) → import '../shared/pricing.js' ได้ทั้งใน docker และนอก docker
FROM node:22-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils fonts-thai-tlwg ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app/workers
COPY workers/package.json workers/package-lock.json* ./
RUN npm install --omit=dev --no-audit --no-fund
COPY shared/ /app/shared/
# เอกสาร PDF ตั้งต้นของ RAG (rag-worker ingest ตอนเริ่ม · ไฟล์เปลี่ยน → ingest ใหม่อัตโนมัติ)
# มาจาก LAB/documents/ ผ่าน build context เพิ่ม "documents" (docker-compose.yml: additional_contexts)
COPY --from=documents *.pdf /app/docs/
COPY workers/ ./
ENV NODE_ENV=production
CMD ["node", "chat-worker.js"]
