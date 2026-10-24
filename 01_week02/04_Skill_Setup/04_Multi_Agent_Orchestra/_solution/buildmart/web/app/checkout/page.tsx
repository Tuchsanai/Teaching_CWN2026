// /checkout (B2) — ชำระเงิน: ข้อมูลผู้สั่ง · สาขา · วันส่ง (7 วันถัดไป ไม่รวมอาทิตย์) · ช่วงเช้า/บ่าย
import type { Metadata } from 'next';
import { BRANCHES, deliveryDates } from '../api/cart/_lib';
import CheckoutView from './CheckoutView';
import '../cart/shop.css';

export const metadata: Metadata = { title: 'ชำระเงิน — บ้านช่าง BuildMart' };
export const dynamic = 'force-dynamic';

export default function CheckoutPage() {
  return (
    <div className="b2-page">
      <h1>ชำระเงิน</h1>
      <p className="b2-sub">ตรวจสอบรายการ เลือกสาขาที่ส่งของ วันและช่วงเวลาส่ง แล้วกดยืนยันสั่งซื้อ</p>
      <CheckoutView branches={BRANCHES.map((b) => ({ ...b }))} dates={deliveryDates()} />
    </div>
  );
}
