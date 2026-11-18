'use client';
// components/three/MascotCanvas.tsx (v3) — ฉากเล็กของมาสคอตในหน้าต่างแชท (ครึ่งตัว · พื้นหลังโปร่ง)
import { Canvas } from '@react-three/fiber';
import { useEffect, useState } from 'react';
import MascotModel from './MascotModel';
import type { Live, MascotState } from './util';

export default function MascotCanvas({
  state,
  ampRef,
  levelRef,
  onReady,
}: {
  state: MascotState;
  ampRef?: Live;
  levelRef?: Live;
  onReady?: () => void;
}) {
  const [visible, setVisible] = useState(true);
  // แท็บซ่อนอยู่ → หยุดวาด ประหยัด CPU/GPU
  useEffect(() => {
    const on = () => setVisible(document.visibilityState !== 'hidden');
    document.addEventListener('visibilitychange', on);
    return () => document.removeEventListener('visibilitychange', on);
  }, []);
  return (
    <Canvas
      dpr={[1, 2]}
      frameloop={visible ? 'always' : 'never'}
      camera={{ position: [0, 1.7, 3.55], fov: 32 }}
      gl={{ antialias: true, alpha: true, powerPreference: 'low-power' }}
      onCreated={({ camera }) => {
        camera.lookAt(0, 1.5, 0);
        onReady?.();
      }}
      style={{ background: 'transparent' }}
    >
      <ambientLight intensity={0.55} />
      <hemisphereLight args={['#dfe9ff', '#2a1a10', 0.7]} />
      <directionalLight position={[2.5, 4, 3]} intensity={2.2} />
      <pointLight position={[-2.5, 1.8, 1.5]} intensity={6} color="#3fd6ff" distance={8} />
      <pointLight position={[2, 1.2, -1.5]} intensity={10} color="#ff7a1c" distance={8} />
      <MascotModel state={state} ampRef={ampRef} levelRef={levelRef} />
    </Canvas>
  );
}
