'use client';
// components/Interactions.tsx (v3) — เอฟเฟกต์ทั้งเว็บแบบ event delegation (ไม่แตะ logic ของหน้าไหน)
// - .tilt : การ์ดเอียงตามเมาส์ + แสงส้มตามตำแหน่งเมาส์ (ตั้ง CSS var --rx --ry --mx --my)
// - .reveal : ค่อย ๆ โผล่ขึ้นตอนเลื่อนถึง (IntersectionObserver ใส่ class .in)
import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export default function Interactions() {
  const path = usePathname();

  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    const fine = window.matchMedia?.('(pointer: fine)').matches;
    if (reduce || !fine) return;
    let active: HTMLElement | null = null;
    let raf = 0;
    const reset = (el: HTMLElement) => {
      el.style.setProperty('--rx', '0deg');
      el.style.setProperty('--ry', '0deg');
    };
    const onMove = (e: PointerEvent) => {
      const el = (e.target as Element | null)?.closest?.('.tilt') as HTMLElement | null;
      if (active && active !== el) reset(active);
      active = el;
      if (!el) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width;
        const y = (e.clientY - r.top) / r.height;
        el.style.setProperty('--ry', `${(x - 0.5) * 9}deg`);
        el.style.setProperty('--rx', `${(0.5 - y) * 9}deg`);
        el.style.setProperty('--mx', `${x * 100}%`);
        el.style.setProperty('--my', `${y * 100}%`);
      });
    };
    const onLeave = () => {
      if (active) reset(active);
      active = null;
    };
    window.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerleave', onLeave);
    return () => {
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerleave', onLeave);
      cancelAnimationFrame(raf);
    };
  }, []);

  useEffect(() => {
    const els = Array.from(document.querySelectorAll<HTMLElement>('.reveal:not(.in)'));
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) {
      els.forEach((el) => el.classList.add('in'));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        for (const en of entries) {
          if (en.isIntersecting) {
            en.target.classList.add('in');
            io.unobserve(en.target);
          }
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.05 },
    );
    els.forEach((el) => io.observe(el));
    // กันกรณี headless/พิมพ์: แสดงทั้งหมดหลัง 2.5 วิ แม้ไม่ได้เลื่อน
    const t = setTimeout(() => els.forEach((el) => el.classList.add('in')), 2500);
    return () => {
      io.disconnect();
      clearTimeout(t);
    };
  }, [path]);

  return null;
}
