'use client';
// components/Hero3D.tsx (v3) — โหลดฉาก Three.js หลัง hydrate (ไม่ถ่วง first paint) · ไม่มี WebGL → เหลือภาพพื้นหลัง + มาสคอตภาพนิ่ง
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import { hasWebGL, prefersReducedMotion } from './three/util';

const HeroScene = dynamic(() => import('./three/HeroScene'), { ssr: false, loading: () => null });

export default function Hero3D() {
  const [mode, setMode] = useState<'pending' | '3d' | 'flat'>('pending');
  const [ready, setReady] = useState(false);
  useEffect(() => {
    setMode(hasWebGL() ? '3d' : 'flat');
  }, []);
  return (
    <div className={`hero3d-canvas${ready ? ' ready' : ''}`} data-testid="hero-3d" data-render={mode === '3d' ? (ready ? '3d' : 'loading') : mode}>
      {mode === '3d' && <HeroScene onReady={() => setReady(true)} />}
      {mode === 'flat' && (
        // eslint-disable-next-line @next/next/no-img-element
        <img className={`hero-flat-mascot${prefersReducedMotion() ? '' : ' bob'}`} src="/img/mascot.webp" alt="" aria-hidden />
      )}
    </div>
  );
}
