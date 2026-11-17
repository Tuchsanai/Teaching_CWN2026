// AI server จำลอง (ไม่ต้องมี GPU) ใช้ทดสอบเว็บ — ตอบรูปแบบ JSON เดียวกับ serve.py
const http = require("http");

// อ่านขนาดรูปจาก header ของไฟล์ JPEG/PNG
function imageSize(buf) {
  if (buf[0] === 0x89 && buf[1] === 0x50) return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xff) { i++; continue; }
    const m = buf[i + 1];
    if (m >= 0xc0 && m <= 0xc3) return { w: buf.readUInt16BE(i + 7), h: buf.readUInt16BE(i + 5) };
    i += 2 + buf.readUInt16BE(i + 2);
  }
  return { w: 640, h: 640 };
}

// ดึงไฟล์แรกออกจาก multipart/form-data
function firstFile(body, boundary) {
  const sep = Buffer.from("--" + boundary);
  const start = body.indexOf(sep);
  const headEnd = body.indexOf(Buffer.from("\r\n\r\n"), start);
  const end = body.indexOf(sep, headEnd);
  return body.subarray(headEnd + 4, end - 2);
}

const box = (cls, conf, x1, y1, x2, y2, w, h) => ({
  class: cls, confidence: conf,
  box: [x1 * w, y1 * h, x2 * w, y2 * h].map((v) => Math.round(v * 10) / 10),
});

http.createServer((req, res) => {
  const send = (code, obj) => { res.writeHead(code, { "content-type": "application/json" }); res.end(JSON.stringify(obj)); };
  if (req.url === "/health") return send(200, { status: "ok", model: "mock-ppe" });
  if (req.method !== "POST" || !req.url.startsWith("/v1/detect")) return send(404, { detail: "not found" });
  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", () => {
    const boundary = (req.headers["content-type"] || "").split("boundary=")[1];
    const { w, h } = imageSize(firstFile(Buffer.concat(chunks), boundary));
    send(200, {
      model: "mock-ppe", width: w, height: h,
      inference_ms: 6 + Math.round(Math.random() * 30) / 10, total_ms: 12.4,
      detections: [
        box("Person", 0.91, 0.08, 0.2, 0.38, 0.95, w, h),
        box("Hardhat", 0.88, 0.17, 0.2, 0.29, 0.32, w, h),
        box("Safety Vest", 0.82, 0.1, 0.4, 0.36, 0.66, w, h),
        box("Person", 0.87, 0.55, 0.25, 0.85, 0.97, w, h),
        box("NO-Hardhat", 0.79, 0.64, 0.25, 0.76, 0.38, w, h),
        box("NO-Safety Vest", 0.71, 0.57, 0.42, 0.83, 0.7, w, h),
      ],
    });
  });
}).listen(8000, () => console.log("mock-yolo on :8000"));
