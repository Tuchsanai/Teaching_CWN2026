// แสดงเงินแบบ ฿1,234 · มีสตางค์แสดง ฿1,187.50 (NFR-17) · ค่าที่รับเป็นสตางค์

export function formatBaht(satang: number): string {
  const neg = satang < 0;
  const a = Math.abs(Math.round(satang));
  const baht = Math.floor(a / 100);
  const st = a % 100;
  const body = baht.toLocaleString("en-US") + (st ? "." + String(st).padStart(2, "0") : "");
  return `${neg ? "-" : ""}฿${body}`;
}

/** สตางค์ → บาท (number) สำหรับ JSON */
export function toBaht(satang: number): number {
  return Math.round(satang) / 100;
}
