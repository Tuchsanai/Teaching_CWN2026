// /calculator (B1) — เครื่องคำนวณวัสดุ 5 แท็บ (สูตร BUILDMART ข้อ 3.3 ใน shared/calc.js)
import CalcApp from '@/components/CalcApp';
import './calculator.css';

export const metadata = { title: 'เครื่องคำนวณวัสดุ — บ้านช่าง BuildMart' };

const TYPES = ['concrete', 'wall', 'tile', 'paint', 'rebar'] as const;

export default function CalculatorPage({ searchParams }: { searchParams: { tab?: string } }) {
  const tab = (TYPES as readonly string[]).includes(searchParams.tab || '') ? (searchParams.tab as (typeof TYPES)[number]) : 'concrete';
  return (
    <div className="calc-page">
      <div className="calc-hero">
        <h1>🧮 เครื่องคำนวณวัสดุ</h1>
        <p>กรอกขนาดงาน ระบบคำนวณจำนวนวัสดุ (ปัดขึ้นเป็นจำนวนเต็ม) จับคู่สินค้าในร้าน แล้วเพิ่มลงตะกร้าได้ในคลิกเดียว</p>
      </div>
      <CalcApp initialTab={tab} />
    </div>
  );
}
