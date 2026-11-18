// ใช้เฉพาะฝั่ง server — key ไม่ถูกส่งไปถึงเบราว์เซอร์
import "server-only";
export const AI_URL = (process.env.YOLO_BASE_URL || "").replace(/\/+$/, "");
export const AI_KEY = process.env.YOLO_API_KEY || "";
