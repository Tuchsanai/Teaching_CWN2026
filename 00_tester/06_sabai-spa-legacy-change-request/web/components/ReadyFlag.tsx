"use client";

import { useEffect } from "react";

/** ตั้ง <html data-ready="true"> หลัง hydrate เสร็จ (ใช้รอในสคริปต์ทดสอบ) */
export function ReadyFlag() {
  useEffect(() => {
    document.documentElement.setAttribute("data-ready", "true");
  }, []);
  return null;
}
