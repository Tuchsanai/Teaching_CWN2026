# mock-llm — build context = ROOT (docker-compose) · ไม่มี dependency
FROM node:22-alpine
# ffmpeg: mock STT ถอดเสียง webm จากไมค์ปลอมของ e2e เพื่อเทียบ fingerprint กับไฟล์ fixture (CONTRACT_V3 §9)
RUN apk add --no-cache ffmpeg
WORKDIR /app
COPY mock-llm/package.json mock-llm/server.js mock-llm/selftest.mjs ./
# v3: ไฟล์เสียงทดสอบ (mock STT: index.json sha256 → ข้อความ · mock TTS: tts-cache/<sha256>.wav ที่อัดจาก VoxCPM2)
#   ไม่มี index.json / tts-cache ก็ทำงานได้ (ได้ตารางว่าง · TTS ใช้เสียงสังเคราะห์สั้น ๆ แทน)
COPY e2e/voice-fixtures/ /app/voice/
ENV VOICE_INDEX=/app/voice/index.json TTS_CACHE_DIR=/app/voice/tts-cache
ENV PORT=8000 NODE_ENV=production
EXPOSE 8000
USER node
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD wget -qO- http://127.0.0.1:8000/health >/dev/null || exit 1
CMD ["node", "server.js"]
