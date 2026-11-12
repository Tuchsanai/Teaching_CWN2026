'use client';
// components/three/Mascot.tsx (v3) — กรอบมาสคอต data-testid="mascot" data-state=idle|listening|thinking|talking
// โหลด Three.js แบบ lazy · ไม่มี WebGL → ใช้ภาพ /img/mascot.webp|png + CSS animation ตาม state แทน
import dynamic from 'next/dynamic';
import { useEffect, useRef, useState } from 'react';
import { hasWebGL, type Live, type MascotState } from './util';

const MascotCanvas = dynamic(() => import('./MascotCanvas'), { ssr: false, loading: () => null });

export default function Mascot({
  state,
  ampRef,
  levelRef,
  className = '',
  testId = 'mascot',
}: {
  state: MascotState;
  ampRef?: Live;
  levelRef?: Live;
  className?: string;
  testId?: string;
}) {
  const [mode, setMode] = useState<'pending' | '3d' | 'img'>('pending');
  const [ready, setReady] = useState(false);
  const [imgSrc, setImgSrc] = useState('/img/mascot.webp');
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => setMode(hasWebGL() ? '3d' : 'img'), []);
  // ทุกโหมด: data-mouth = ความเปิดของปาก 0.00–1.00 (เฉพาะตอนพูด) ให้ e2e ตรวจ lip-sync
  // โหมดภาพนิ่ง: ส่งความดังเสียงเป็น CSS var --amp / --lvl ให้ CSS animation ใช้ด้วย
  const stateRef = useRef(state);
  stateRef.current = state;
  useEffect(() => {
    let raf = 0;
    let mouth = 0;
    let last = '';
    let prev = performance.now();
    const tick = (now: number) => {
      const dt = Math.min(0.05, (now - prev) / 1000);
      prev = now;
      const el = box.current;
      const target = stateRef.current === 'talking' ? Math.max(0, Math.min(1, ampRef?.current ?? 0)) : 0;
      mouth += (target - mouth) * (1 - Math.exp(-18 * dt));
      if (el) {
        const m = mouth < 0.005 ? '0.00' : mouth.toFixed(2);
        if (m !== last) {
          el.setAttribute('data-mouth', m);
          el.style.setProperty('--amp', m);
          last = m;
        }
        el.style.setProperty('--lvl', Math.min(1, levelRef?.current ?? 0).toFixed(2));
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [ampRef, levelRef]);

  return (
    <div
      ref={box}
      className={`mascot mascot-${state} ${className}`}
      data-testid={testId}
      data-state={state}
      data-render={mode === '3d' ? (ready ? '3d' : 'loading') : mode}
      aria-label={`น้องช่าง (${state})`}
      role="img"
    >
      {(mode === 'img' || (mode === '3d' && !ready)) && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          className="mascot-img"
          src={imgSrc}
          alt=""
          onError={() => setImgSrc((s) => (s.endsWith('.webp') ? '/img/mascot.png' : s))}
        />
      )}
      {mode === '3d' && (
        <div className={`mascot-gl${ready ? ' on' : ''}`}>
          <MascotCanvas state={state} ampRef={ampRef} levelRef={levelRef} onReady={() => setReady(true)} />
        </div>
      )}
      {state === 'listening' && <span className="mascot-wave" aria-hidden />}
    </div>
  );
}
