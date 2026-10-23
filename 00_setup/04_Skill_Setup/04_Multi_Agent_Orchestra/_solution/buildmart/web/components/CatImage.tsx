'use client';
// components/CatImage.tsx (v3) — รูปหมวดสินค้า /img/cat-*.png · ไม่มีไฟล์/โหลดไม่ได้ → แสดง emoji แทน
import { useEffect, useRef, useState } from 'react';
import { CATEGORIES } from '@/lib/categories';

const FILE: Record<string, string> = {
  'ปูน': 'cement',
  'หิน-ทราย': 'aggregate',
  'เหล็ก': 'steel',
  'อิฐ-บล็อก': 'brick',
  'กระเบื้อง': 'tile',
  'สี': 'paint',
  'ประปา': 'plumbing',
  'ไฟฟ้า': 'electric',
  'หลังคา': 'roof',
  'ไม้': 'wood',
  'เครื่องมือ': 'tools',
};

/** ไฟล์ที่ลองตามลำดับ: .webp (ย่อแล้ว ~40 KB) → .png (ต้นฉบับ) */
export function catImageSrcs(category: string): string[] {
  const f = FILE[category];
  return f ? [`/img/cat-${f}.webp`, `/img/cat-${f}.png`] : [];
}

export function catEmoji(category: string): string {
  return CATEGORIES.find((c) => c.name === category)?.icon || '📦';
}

/** หมวดจากรหัส SKU (ใช้เมื่อไม่รู้หมวด เช่น แถวตะกร้า/ชิปสินค้าในแชท) */
const PREFIX: Record<string, string> = {
  CEM: 'ปูน',
  AGG: 'หิน-ทราย',
  STL: 'เหล็ก',
  BRK: 'อิฐ-บล็อก',
  TIL: 'กระเบื้อง',
  PNT: 'สี',
  PIP: 'ประปา',
  ELC: 'ไฟฟ้า',
  ROF: 'หลังคา',
  WOD: 'ไม้',
  TOL: 'เครื่องมือ',
};
export const categoryOfSku = (sku: string) => PREFIX[String(sku).slice(0, 3).toUpperCase()] || '';

/** รูปสินค้ารายตัว: /img/products/<SKU>.webp → .png → รูปหมวด (.webp → .png) → emoji */
export function ProductImage({
  sku,
  category,
  className = '',
  fallbackClassName = '',
}: {
  sku: string;
  category?: string;
  className?: string;
  fallbackClassName?: string;
}) {
  const cat = category || categoryOfSku(sku);
  const enc = encodeURIComponent(sku);
  return (
    <ImgChain
      key={sku}
      srcs={[`/img/products/${enc}.webp`, `/img/products/${enc}.png`, ...catImageSrcs(cat)]}
      emoji={catEmoji(cat)}
      className={className}
      fallbackClassName={fallbackClassName}
    />
  );
}

export default function CatImage({
  category,
  className = '',
  fallbackClassName = '',
  onMissing,
}: {
  category: string;
  className?: string;
  fallbackClassName?: string;
  onMissing?: () => void;
}) {
  return (
    <ImgChain
      srcs={catImageSrcs(category)}
      emoji={catEmoji(category)}
      className={className}
      fallbackClassName={fallbackClassName}
      onMissing={onMissing}
    />
  );
}

/** ลองโหลดรูปตามลำดับ srcs · หมดแล้วแสดง emoji */
function ImgChain({
  srcs,
  emoji,
  className = '',
  fallbackClassName = '',
  onMissing,
}: {
  srcs: string[];
  emoji: string;
  className?: string;
  fallbackClassName?: string;
  onMissing?: () => void;
}) {
  const [idx, setIdx] = useState(0);
  const src = srcs[idx];
  const failed = !src;
  const ref = useRef<HTMLImageElement>(null);
  const next = () => setIdx((i) => i + 1);

  // error ที่เกิดก่อน hydrate จะไม่เรียก onError → ตรวจซ้ำหลัง mount
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) next();
  }, [idx]);
  useEffect(() => {
    if (failed) onMissing?.();
  }, [failed, onMissing]);

  if (failed)
    return (
      <span className={`cat-emoji ${fallbackClassName}`} aria-hidden>
        {emoji}
      </span>
    );
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img key={src} ref={ref} src={src} alt="" aria-hidden className={className} loading="lazy" decoding="async" onError={next} />
  );
}
