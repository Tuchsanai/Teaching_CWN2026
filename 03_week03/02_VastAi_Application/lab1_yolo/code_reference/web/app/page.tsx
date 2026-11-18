import Inspector from "@/components/Inspector";

export default function Home() {
  return (
    <>
      <div className="page-head">
        <h1>ตรวจความปลอดภัยหน้างาน</h1>
        <p className="muted">ส่งภาพจากหน้างาน ระบบจะตีกรอบคน หมวกนิรภัย และเสื้อสะท้อนแสง แล้วตัดสินว่าผ่านหรือไม่ผ่าน</p>
      </div>
      <Inspector />
    </>
  );
}
