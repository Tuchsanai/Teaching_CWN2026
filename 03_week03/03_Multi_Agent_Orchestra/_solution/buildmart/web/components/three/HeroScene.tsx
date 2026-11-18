'use client';
// components/three/HeroScene.tsx (v3) — ฉาก 3D หน้าแรก: วัสดุก่อสร้างลอย (อิฐ ถุงปูน เหล็กเส้น ท่อ ถังสี กระเบื้อง)
// + น้องช่างยืนโบกมือบนแท่นเรืองแสง · เมาส์ = parallax · เลื่อนหน้า = กล้องถอย/ก้ม วัสดุกระจายออก
// สร้างจาก primitive ทั้งหมด (ไม่โหลดโมเดล) · หยุดวาดเมื่อเลื่อนพ้น hero หรือแท็บซ่อน
import { Environment, Lightformer, RoundedBox, Sparkles } from '@react-three/drei';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import MascotModel, { glowTexture } from './MascotModel';
import { damp } from './util';

type Kind = 'brick' | 'bag' | 'rebar' | 'pipe' | 'elbow' | 'bucket' | 'tile';
type Item = { kind: Kind; pos: THREE.Vector3; rot: THREE.Euler; spin: THREE.Vector3; amp: number; speed: number; phase: number; scale: number; variant: number };

function rng(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const PLAN: [Kind, number][] = [
  ['brick', 8],
  ['bag', 4],
  ['rebar', 4],
  ['pipe', 3],
  ['elbow', 2],
  ['bucket', 3],
  ['tile', 5],
];

function useItems(compact: boolean) {
  return useMemo(() => {
    const r = rng(20261023);
    const out: Item[] = [];
    for (const [kind, n] of PLAN) {
      for (let i = 0; i < (compact ? Math.ceil(n * 0.6) : n); i++) {
        let pos: THREE.Vector3;
        let tries = 0;
        do {
          pos = compact
            ? new THREE.Vector3(-2.2 + r() * 4.4, -0.6 + r() * 4.4, -5 + r() * 5.5)
            : new THREE.Vector3(1.7 + r() * 6, -3 + r() * 6.2, -6 + r() * 8);
          tries++;
          // ฝั่งซ้าย (หลังข้อความ) ให้อยู่ลึก ๆ จางในหมอก ไม่บังตัวหนังสือ
          if (compact && pos.z > -2.5 && pos.y > 0.4) pos.z = -3 - r() * 2.5;
          // เว้นที่ให้มาสคอต
        } while (tries < 30 && Math.hypot(pos.x - (compact ? 0.9 : 2.8), (pos.y - (compact ? -2.2 : -0.6)) * 0.7) < 1.7 && pos.z > -2);
        out.push({
          kind,
          pos,
          rot: new THREE.Euler(r() * Math.PI, r() * Math.PI, r() * Math.PI),
          spin: new THREE.Vector3((r() - 0.5) * 0.5, (r() - 0.5) * 0.5, (r() - 0.5) * 0.3),
          amp: 0.1 + r() * 0.22,
          speed: 0.5 + r() * 0.7,
          phase: r() * Math.PI * 2,
          scale: 0.8 + r() * 0.5,
          variant: Math.floor(r() * 3),
        });
      }
    }
    return out;
  }, [compact]);
}

function useMaterials() {
  return useMemo(
    () => ({
      brick: [
        new THREE.MeshStandardMaterial({ color: '#c9532f', roughness: 0.85 }),
        new THREE.MeshStandardMaterial({ color: '#b5452a', roughness: 0.9 }),
        new THREE.MeshStandardMaterial({ color: '#cfc8bd', roughness: 0.95 }),
      ],
      hole: new THREE.MeshStandardMaterial({ color: '#3a1a10', roughness: 1 }),
      kraft: new THREE.MeshStandardMaterial({ color: '#c8ad86', roughness: 0.95 }),
      band: new THREE.MeshStandardMaterial({ color: '#f26b1d', roughness: 0.6, emissive: '#f26b1d', emissiveIntensity: 0.12 }),
      steel: new THREE.MeshStandardMaterial({ color: '#4d535c', roughness: 0.42, metalness: 0.85 }),
      wire: new THREE.MeshStandardMaterial({ color: '#2b2e33', roughness: 0.5, metalness: 0.7 }),
      pvc: new THREE.MeshPhysicalMaterial({ color: '#eef0f2', roughness: 0.3, clearcoat: 0.5, side: THREE.DoubleSide }),
      pvcBlue: new THREE.MeshPhysicalMaterial({ color: '#3b6fd8', roughness: 0.35, clearcoat: 0.4, side: THREE.DoubleSide }),
      tin: new THREE.MeshStandardMaterial({ color: '#e7e8eb', roughness: 0.28, metalness: 0.55 }),
      orange: new THREE.MeshPhysicalMaterial({ color: '#ff7a1c', roughness: 0.3, clearcoat: 0.6 }),
      paint: new THREE.MeshStandardMaterial({ color: '#ff8a3d', roughness: 0.2, emissive: '#f26b1d', emissiveIntensity: 0.25 }),
      tile: [
        new THREE.MeshPhysicalMaterial({ color: '#dcd8d0', roughness: 0.18, clearcoat: 0.8 }),
        new THREE.MeshPhysicalMaterial({ color: '#5d5853', roughness: 0.22, clearcoat: 0.8 }),
        new THREE.MeshStandardMaterial({ color: '#c46a42', roughness: 0.7 }),
      ],
    }),
    [],
  );
}

type Mats = ReturnType<typeof useMaterials>;

function Thing({ it, m }: { it: Item; m: Mats }) {
  switch (it.kind) {
    case 'brick':
      return (
        <group>
          <RoundedBox args={[0.62, 0.2, 0.3]} radius={0.025} smoothness={2} material={m.brick[it.variant]} />
          {it.variant !== 2 &&
            [-0.18, 0, 0.18].map((x) => (
              <mesh key={x} position={[x, 0.101, 0]} rotation={[-Math.PI / 2, 0, 0]} material={m.hole}>
                <circleGeometry args={[0.055, 16]} />
              </mesh>
            ))}
        </group>
      );
    case 'bag':
      return (
        <group>
          <RoundedBox args={[0.62, 0.86, 0.26]} radius={0.11} smoothness={4} material={m.kraft} />
          <mesh position={[0, -0.06, 0]} material={m.band}>
            <boxGeometry args={[0.6, 0.2, 0.275]} />
          </mesh>
        </group>
      );
    case 'rebar':
      return (
        <group>
          {[
            [-0.05, -0.05],
            [0.05, -0.05],
            [-0.05, 0.05],
            [0.05, 0.05],
            [0, 0.12],
          ].map(([x, z], i) => (
            <mesh key={i} position={[x, (i % 2) * 0.08, z]} material={m.steel}>
              <cylinderGeometry args={[0.032, 0.032, 2.4, 10]} />
            </mesh>
          ))}
          {[-0.6, 0.6].map((y) => (
            <mesh key={y} position={[0, y, 0.02]} rotation={[Math.PI / 2, 0, 0]} material={m.wire}>
              <torusGeometry args={[0.13, 0.014, 6, 20]} />
            </mesh>
          ))}
        </group>
      );
    case 'pipe':
      return (
        <group>
          <mesh material={it.variant === 0 ? m.pvcBlue : m.pvc}>
            <cylinderGeometry args={[0.13, 0.13, 1.4, 28, 1, true]} />
          </mesh>
          {[-0.7, 0.7].map((y) => (
            <mesh key={y} position={[0, y, 0]} material={m.pvc}>
              <cylinderGeometry args={[0.16, 0.16, 0.16, 28, 1, true]} />
            </mesh>
          ))}
        </group>
      );
    case 'elbow':
      return (
        <mesh material={m.pvc}>
          <torusGeometry args={[0.3, 0.13, 16, 28, Math.PI / 2]} />
        </mesh>
      );
    case 'bucket':
      return (
        <group>
          <mesh material={m.tin}>
            <cylinderGeometry args={[0.32, 0.27, 0.56, 32]} />
          </mesh>
          <mesh position={[0, -0.02, 0]} material={m.orange}>
            <cylinderGeometry args={[0.31, 0.295, 0.18, 32]} />
          </mesh>
          <mesh position={[0, 0.3, 0]} material={it.variant === 1 ? m.paint : m.orange}>
            <cylinderGeometry args={[0.335, 0.335, 0.05, 32]} />
          </mesh>
          <mesh position={[0, 0.3, 0]} rotation={[0, 0, 0]} material={m.wire}>
            <torusGeometry args={[0.32, 0.012, 6, 24, Math.PI]} />
          </mesh>
        </group>
      );
    case 'tile':
      return <RoundedBox args={[0.72, 0.05, 0.72]} radius={0.015} smoothness={2} material={m.tile[it.variant]} />;
  }
}

function Materials({ compact, scrollRef }: { compact: boolean; scrollRef: React.MutableRefObject<number> }) {
  const items = useItems(compact);
  const m = useMaterials();
  const refs = useRef<(THREE.Group | null)[]>([]);
  const group = useRef<THREE.Group>(null);
  useFrame((st, dtRaw) => {
    const dt = Math.min(dtRaw, 0.05);
    const t = st.clock.elapsedTime;
    const p = scrollRef.current;
    items.forEach((it, i) => {
      const g = refs.current[i];
      if (!g) return;
      const spread = 1 + p * 0.55;
      g.position.set(
        it.pos.x * spread + (it.pos.x > 2.8 ? p * 1.2 : -p * 0.4),
        it.pos.y * spread + Math.sin(t * it.speed + it.phase) * it.amp,
        it.pos.z + p * 1.5,
      );
      g.rotation.x += it.spin.x * dt;
      g.rotation.y += it.spin.y * dt;
      g.rotation.z += it.spin.z * dt;
    });
    if (group.current) group.current.rotation.y = damp(group.current.rotation.y, p * 0.35, 4, dt);
  });
  return (
    <group ref={group}>
      {items.map((it, i) => (
        <group key={i} ref={(el) => {
            refs.current[i] = el;
          }} rotation={it.rot} scale={it.scale}>
          <Thing it={it} m={m} />
        </group>
      ))}
    </group>
  );
}

function Rig({ compact, scrollRef, pointer }: { compact: boolean; scrollRef: React.MutableRefObject<number>; pointer: React.MutableRefObject<[number, number]> }) {
  const { camera } = useThree();
  const look = useMemo(() => new THREE.Vector3(), []);
  useFrame((_, dtRaw) => {
    const dt = Math.min(dtRaw, 0.05);
    const p = scrollRef.current;
    const [px, py] = pointer.current;
    const baseX = compact ? 0 : 0.6;
    camera.position.x = damp(camera.position.x, baseX + px * 0.7, 3, dt);
    camera.position.y = damp(camera.position.y, 0.5 + py * 0.35 - p * 2.2, 3, dt);
    camera.position.z = damp(camera.position.z, (compact ? 11 : 9) + p * 2.5, 3, dt);
    look.set(compact ? 0 : 1.1, -0.2 - p * 1.4, 0);
    camera.lookAt(look);
  });
  return null;
}

function Stage({ compact }: { compact: boolean }) {
  const glow = useMemo(() => glowTexture(), []);
  const ring = useRef<THREE.Mesh>(null);
  const ring2 = useRef<THREE.Mesh>(null);
  useFrame((st) => {
    const t = st.clock.elapsedTime;
    if (ring.current) ring.current.rotation.z = t * 0.4;
    if (ring2.current) {
      const k = 1 + ((t * 0.5) % 1) * 0.6;
      ring2.current.scale.set(k, k, k);
      (ring2.current.material as THREE.MeshBasicMaterial).opacity = 0.5 * (1 - ((t * 0.5) % 1));
    }
  });
  const x = compact ? 0.9 : 2.8;
  const y = compact ? -3.2 : -2.15;
  const s = compact ? 1.05 : 1.45;
  return (
    <group>
      <MascotModel state="idle" wave position={[x, y, 0.4]} scale={s} />
      <group position={[x, y + 0.01, 0.4]} rotation={[-Math.PI / 2, 0, 0]}>
        <mesh>
          <circleGeometry args={[1.25 * s, 48]} />
          <meshBasicMaterial map={glow} color="#3fd6ff" transparent opacity={0.55} depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
        </mesh>
        <mesh ref={ring}>
          <ringGeometry args={[0.78 * s, 0.81 * s, 64, 1, 0, Math.PI * 1.6]} />
          <meshBasicMaterial color="#68f1ff" transparent opacity={0.9} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
        <mesh ref={ring2}>
          <ringGeometry args={[0.6 * s, 0.62 * s, 64]} />
          <meshBasicMaterial color="#ff8a3d" transparent opacity={0.5} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      </group>
      <sprite position={[x, y + 1.6 * s, -1.2]} scale={[5.5 * s, 5.5 * s, 1]}>
        <spriteMaterial map={glow} color="#f26b1d" transparent opacity={0.28} depthWrite={false} blending={THREE.AdditiveBlending} />
      </sprite>
    </group>
  );
}

export default function HeroScene({ onReady }: { onReady?: () => void }) {
  const wrap = useRef<HTMLDivElement>(null);
  const scrollRef = useRef(0);
  const pointer = useRef<[number, number]>([0, 0]);
  const [active, setActive] = useState(true);
  const [compact, setCompact] = useState(false);

  useEffect(() => {
    const el = wrap.current;
    const onResize = () => setCompact(window.innerWidth < 860);
    const onScroll = () => {
      const h = el?.parentElement?.offsetHeight || window.innerHeight;
      scrollRef.current = Math.max(0, Math.min(1, window.scrollY / h));
    };
    const onMove = (e: PointerEvent) => {
      pointer.current = [(e.clientX / window.innerWidth) * 2 - 1, -((e.clientY / window.innerHeight) * 2 - 1)];
    };
    let inView = true;
    const sync = () => setActive(inView && document.visibilityState !== 'hidden');
    const io = new IntersectionObserver(([en]) => {
      inView = en.isIntersecting;
      sync();
    });
    if (el) io.observe(el);
    onResize();
    onScroll();
    window.addEventListener('resize', onResize);
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('visibilitychange', sync);
    return () => {
      io.disconnect();
      window.removeEventListener('resize', onResize);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('visibilitychange', sync);
    };
  }, []);

  return (
    <div ref={wrap} style={{ position: 'absolute', inset: 0 }}>
      <Canvas
        dpr={[1, 1.75]}
        frameloop={active ? 'always' : 'never'}
        camera={{ position: [0.6, 0.5, 9], fov: 38, near: 0.1, far: 60 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping;
          gl.toneMappingExposure = 1.05;
          onReady?.();
        }}
      >
        <fog attach="fog" args={['#0c1017', 9, 24]} />
        <ambientLight intensity={0.35} />
        <hemisphereLight args={['#cfe0ff', '#3a1d0c', 0.55]} />
        <directionalLight position={[-4, 6, 6]} intensity={2.4} color="#fff4e8" />
        <pointLight position={[5, 1, -2]} intensity={60} distance={14} color="#ff7a1c" />
        <pointLight position={[-3, -1, 3]} intensity={25} distance={12} color="#3fd6ff" />
        <Environment resolution={128} frames={1}>
          <Lightformer form="rect" intensity={2.2} position={[0, 5, -6]} scale={[12, 3, 1]} />
          <Lightformer form="rect" intensity={1.4} color="#ff8a3d" position={[6, 0, 2]} rotation={[0, -Math.PI / 2, 0]} scale={[6, 4, 1]} />
          <Lightformer form="rect" intensity={1} color="#3fd6ff" position={[-6, 1, 2]} rotation={[0, Math.PI / 2, 0]} scale={[6, 4, 1]} />
        </Environment>
        <Rig compact={compact} scrollRef={scrollRef} pointer={pointer} />
        <Materials compact={compact} scrollRef={scrollRef} />
        {!compact && <Stage compact={compact} />}
        <Sparkles count={compact ? 40 : 90} scale={[16, 9, 10]} position={[1.5, 0, -2]} size={3.2} speed={0.35} opacity={0.75} color="#ff9a55" />
        <Sparkles count={compact ? 15 : 30} scale={[12, 8, 6]} position={[2, 0, 0]} size={2} speed={0.25} opacity={0.5} color="#68f1ff" />
      </Canvas>
    </div>
  );
}
