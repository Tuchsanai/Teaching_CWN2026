import Inspector from "@/components/Inspector";

export default function Home() {
  return (
    <>
      <div className="page-head">
        <h1>ตรวจความปลอดภัยหน้างาน</h1>
        <p className="muted">ส่งรูปถ่ายหน้างานให้โมเดล YOLO ตรวจหมวกนิรภัยและเสื้อสะท้อนแสง ผลทุกครั้งถูกบันทึกในหน้าประวัติ</p>
      </div>
      <Inspector />
    </>
  );
}
