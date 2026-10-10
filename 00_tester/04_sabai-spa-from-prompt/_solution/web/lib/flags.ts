// ค่าตั้งของระบบที่อ่านจาก env จุดเดียว (ทั้งฝั่งกฎร้านและ API)

const mode = (): string => (typeof process !== "undefined" && process.env.BUG_MODE) || "0";

export type PriceStep = "percent" | "points";

export const flags = {
  get bugMode(): "0" | "1" {
    return mode() === "1" ? "1" : "0";
  },
  get allowTestReset(): boolean {
    return (process.env.ALLOW_TEST_RESET ?? "1") === "1";
  },
  /** นาทีเผื่อเก็บห้องก่อนปิดร้าน */
  get closingBufferMin(): number {
    return mode() === "1" ? 1 : 0;
  },
  /** ลำดับขั้นหักส่วนลดก่อนบวกค่ารถ */
  get priceSteps(): PriceStep[] {
    return mode() === "1" ? ["points", "percent"] : ["percent", "points"];
  },
  /** ยอดที่ใช้เป็นฐานคิดแต้ม */
  get loyaltyBasis(): "net" | "list" {
    return mode() === "1" ? "list" : "net";
  },
};
