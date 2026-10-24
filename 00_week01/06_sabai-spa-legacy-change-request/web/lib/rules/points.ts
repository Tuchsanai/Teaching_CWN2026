// BR-09 แต้ม = floor(ยอดจ่าย ÷ 100) · BR-10 แลก 100 แต้ม = ลด ฿50 เป็นก้อนเท่านั้น (เงินเป็นสตางค์)

export const POINT_BLOCK = 100;
export const BLOCK_VALUE = 50_00;

export function pointsFor(amount: number): number {
  return amount > 0 ? Math.floor(amount / 100_00) : 0;
}

export function maxRedeemBlocks(points: number): number {
  return Math.max(0, Math.floor(points / POINT_BLOCK));
}

/** หักแต้มจากยอด: ไม่เกินก้อนที่มี ไม่ทำให้ยอดติดลบ (A9) และไม่ใช้ก้อนเกินจำเป็น */
export function redeemPoints(requestedBlocks: number, points: number, amount: number): { blocks: number; discount: number } {
  const needed = Math.ceil(Math.max(0, amount) / BLOCK_VALUE);
  const blocks = Math.max(0, Math.min(requestedBlocks, maxRedeemBlocks(points), needed));
  return { blocks, discount: Math.min(blocks * BLOCK_VALUE, Math.max(0, amount)) };
}

export interface EarnInput {
  gross: number;
  discountAmount: number;
  pointsDiscount: number;
  giftcardPaid: number;
}

/** ฐานแต้ม = ยอดหลังส่วนลดและแต้ม ไม่รวมค่ารถ − ส่วนที่จ่ายด้วย Gift Card (A8, T16) */
export function earnBase(b: EarnInput): number {
  return Math.max(0, b.gross - b.discountAmount - b.pointsDiscount - b.giftcardPaid);
}
