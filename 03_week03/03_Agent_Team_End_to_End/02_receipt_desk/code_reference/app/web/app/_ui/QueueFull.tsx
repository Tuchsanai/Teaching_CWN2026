/**
 * ข้อความคิวเต็ม (FR-22 · BR-11 · BR-12): "ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก N นาที"
 * - องค์ประกอบ `testId` มีเฉพาะประโยคนี้ (ทดสอบเทียบข้อความทั้งประโยคได้ตรง)
 * - N อยู่ในองค์ประกอบแยก (`minutesTestId`) เพื่อให้ทดสอบอ่านตัวเลขได้ตรง
 */
export default function QueueFull({
  minutes,
  testId,
  minutesTestId,
}: {
  minutes: number | undefined;
  testId: string;
  minutesTestId?: string;
}) {
  return (
    <div className="notice warn" role="alert">
      <div data-testid={testId}>
        ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก <strong data-testid={minutesTestId}>{minutes ?? '?'}</strong> นาที
      </div>
      <div className="muted" style={{ fontSize: 13, marginTop: 4 }}>
        ชุดนี้ยังไม่ถูกรับเลยแม้แต่ใบเดียว กรุณาส่งทั้งชุดใหม่อีกครั้ง
      </div>
    </div>
  );
}
