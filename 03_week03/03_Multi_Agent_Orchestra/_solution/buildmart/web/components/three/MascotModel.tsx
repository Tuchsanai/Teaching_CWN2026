'use client';
// components/three/MascotModel.tsx (v3) — มาสคอต "น้องช่าง" แบบ procedural (ไม่มีไฟล์โมเดล)
// ตามภาพ mascot-sheet: หุ่นยนต์ขาวกลม ๆ · หมวกนิรภัยสีส้ม + ไฟฉายคาดหัว · จอหน้าสีดำ ตาฟ้าเรืองแสง ปากบนจอ
// · หูฟังส้ม · เอี๊ยมยีนส์ · เข็มขัดเครื่องมือ (ค้อน/ตลับเมตร) · ถุงมือ/รองเท้าส้ม
// ท่าทาง: idle (ลอยขึ้นลง + กะพริบตา) · listening (โน้มตัว ยกมือแนบหู หูฟังเรืองตามเสียงไมค์)
//        thinking (ตากลายเป็นเฟืองหมุน มือจับคาง) · talking (ปากเปิดตามความดังเสียงจริง)
import { useFrame } from '@react-three/fiber';
import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { damp, type Live, type MascotState } from './util';

function makeGlowTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d')!;
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, 'rgba(255,255,255,1)');
  gr.addColorStop(0.25, 'rgba(255,255,255,0.55)');
  gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr;
  g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function makeDenimTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d')!;
  g.fillStyle = '#34548f';
  g.fillRect(0, 0, 128, 128);
  for (let i = -128; i < 256; i += 4) {
    g.strokeStyle = i % 8 === 0 ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,30,0.12)';
    g.lineWidth = 2;
    g.beginPath();
    g.moveTo(i, 0);
    g.lineTo(i + 128, 128);
    g.stroke();
  }
  for (let i = 0; i < 900; i++) {
    g.fillStyle = `rgba(255,255,255,${Math.random() * 0.06})`;
    g.fillRect(Math.random() * 128, Math.random() * 128, 1, 1);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 3);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

let glowTex: THREE.Texture | null = null;
export function glowTexture() {
  if (!glowTex) glowTex = makeGlowTexture();
  return glowTex;
}

function Gear({ position, gref }: { position: [number, number, number]; gref: React.RefObject<THREE.Group> }) {
  const teeth = Array.from({ length: 8 }, (_, i) => (i / 8) * Math.PI * 2);
  return (
    <group ref={gref} position={position} scale={0.085} visible={false}>
      <mesh>
        <torusGeometry args={[0.62, 0.2, 10, 28]} />
        <meshBasicMaterial color="#6ff3ff" toneMapped={false} />
      </mesh>
      {teeth.map((a) => (
        <mesh key={a} position={[Math.cos(a) * 0.86, Math.sin(a) * 0.86, 0]} rotation={[0, 0, a]}>
          <boxGeometry args={[0.32, 0.3, 0.2]} />
          <meshBasicMaterial color="#6ff3ff" toneMapped={false} />
        </mesh>
      ))}
    </group>
  );
}

export default function MascotModel({
  state,
  ampRef,
  levelRef,
  wave = false,
  position = [0, 0, 0],
  scale = 1,
}: {
  state: MascotState;
  ampRef?: Live;
  levelRef?: Live;
  wave?: boolean;
  position?: [number, number, number];
  scale?: number;
}) {
  const root = useRef<THREE.Group>(null);
  const body = useRef<THREE.Group>(null);
  const head = useRef<THREE.Group>(null);
  const armL = useRef<THREE.Group>(null);
  const armR = useRef<THREE.Group>(null);
  const eyes = useRef<THREE.Group>(null);
  const eyeL = useRef<THREE.Mesh>(null);
  const eyeR = useRef<THREE.Mesh>(null);
  const gearL = useRef<THREE.Group>(null);
  const gearR = useRef<THREE.Group>(null);
  const smile = useRef<THREE.Mesh>(null);
  const mouth = useRef<THREE.Mesh>(null);
  const flat = useRef<THREE.Mesh>(null);
  const earGlowL = useRef<THREE.Sprite>(null);
  const earGlowR = useRef<THREE.Sprite>(null);
  const earMat = useRef<THREE.MeshStandardMaterial>(null);
  const lampGlow = useRef<THREE.Sprite>(null);
  const eyeGlow = useRef<THREE.Sprite>(null);
  const sim = useRef({ blinkAt: 2, blink: 0, amp: 0, lvl: 0, t0: Math.random() * 10 });

  const M = useMemo(() => {
    const denim = makeDenimTexture();
    return {
      white: new THREE.MeshPhysicalMaterial({ color: '#f3efe9', roughness: 0.32, clearcoat: 0.9, clearcoatRoughness: 0.18 }),
      visor: new THREE.MeshPhysicalMaterial({ color: '#04060b', roughness: 0.06, metalness: 0.3, clearcoat: 1, clearcoatRoughness: 0.05 }),
      orange: new THREE.MeshPhysicalMaterial({ color: '#ff7a1c', roughness: 0.34, clearcoat: 0.7, clearcoatRoughness: 0.25 }),
      orangeSoft: new THREE.MeshStandardMaterial({ color: '#f27420', roughness: 0.75 }),
      denim: new THREE.MeshStandardMaterial({ map: denim, color: '#ffffff', roughness: 0.92 }),
      dark: new THREE.MeshStandardMaterial({ color: '#23262e', roughness: 0.55, metalness: 0.2 }),
      grey: new THREE.MeshStandardMaterial({ color: '#b9bdc4', roughness: 0.3, metalness: 0.6 }),
      gold: new THREE.MeshStandardMaterial({ color: '#d6a24a', roughness: 0.3, metalness: 0.85 }),
      wood: new THREE.MeshStandardMaterial({ color: '#b97c43', roughness: 0.6 }),
      steel: new THREE.MeshStandardMaterial({ color: '#8d949f', roughness: 0.25, metalness: 0.9 }),
      sole: new THREE.MeshStandardMaterial({ color: '#2a2320', roughness: 0.85 }),
      cyan: new THREE.MeshBasicMaterial({ color: '#68f1ff', toneMapped: false }),
      lens: new THREE.MeshBasicMaterial({ color: '#fff3c4', toneMapped: false }),
      yellow: new THREE.MeshStandardMaterial({ color: '#ffd23a', roughness: 0.4 }),
    };
  }, []);
  const glow = useMemo(() => (typeof document !== 'undefined' ? glowTexture() : null), []);

  useFrame((st, dtRaw) => {
    const dt = Math.min(dtRaw, 0.05);
    const s = sim.current;
    const t = st.clock.elapsedTime + s.t0;
    const ampIn = Math.max(0, Math.min(1, ampRef?.current ?? 0));
    const lvlIn = Math.max(0, Math.min(1, levelRef?.current ?? 0));
    s.amp = damp(s.amp, ampIn, 18, dt);
    s.lvl = damp(s.lvl, lvlIn, 14, dt);
    const talking = state === 'talking';
    const thinking = state === 'thinking';
    const listening = state === 'listening';

    // ลอยขึ้นลง + หายใจ
    if (root.current) {
      root.current.position.y = position[1] + Math.sin(t * 2.1) * 0.035 * scale + (talking ? s.amp * 0.03 * scale : 0);
    }
    if (body.current) {
      const lean = listening ? 0.16 : thinking ? 0.05 : 0;
      body.current.rotation.x = damp(body.current.rotation.x, lean, 6, dt);
      body.current.rotation.z = damp(body.current.rotation.z, Math.sin(t * 1.1) * 0.03, 4, dt);
      const sy = 1 + Math.sin(t * 2.1) * 0.012;
      body.current.scale.set(1 / Math.sqrt(sy), sy, 1 / Math.sqrt(sy));
    }
    if (head.current) {
      const ty = listening ? 0.28 : thinking ? -0.22 : talking ? Math.sin(t * 1.7) * 0.12 : Math.sin(t * 0.7) * 0.2;
      const tz = listening ? 0.2 : thinking ? -0.16 : talking ? Math.sin(t * 2.3) * 0.05 : Math.sin(t * 0.9) * 0.05;
      const tx = thinking ? -0.12 : talking ? -s.amp * 0.12 : listening ? 0.05 : 0;
      head.current.rotation.y = damp(head.current.rotation.y, ty, 5, dt);
      head.current.rotation.z = damp(head.current.rotation.z, tz, 5, dt);
      head.current.rotation.x = damp(head.current.rotation.x, tx, 8, dt);
    }
    // แขน: [rotX, rotZ]
    let lx = 0, lz = -0.32, rx = 0, rz = 0.32;
    if (wave && state === 'idle') {
      rz = 2.55 + Math.sin(t * 7) * 0.32;
      rx = -0.2;
    } else if (listening) {
      rz = 2.45;
      rx = -0.55;
      lz = -0.5;
    } else if (thinking) {
      rx = -2.15;
      rz = -0.45;
      lz = -0.25;
      lx = -0.3;
    } else if (talking) {
      rz = 0.85 + Math.sin(t * 3.2) * 0.25 + s.amp * 0.4;
      rx = -0.7;
      lz = -0.55 - Math.sin(t * 2.7 + 1) * 0.2;
      lx = -0.3;
    } else {
      rz += Math.sin(t * 2.1 + 0.5) * 0.05;
      lz -= Math.sin(t * 2.1 + 0.5) * 0.05;
    }
    if (armL.current) {
      armL.current.rotation.x = damp(armL.current.rotation.x, lx, 7, dt);
      armL.current.rotation.z = damp(armL.current.rotation.z, lz, 7, dt);
    }
    if (armR.current) {
      armR.current.rotation.x = damp(armR.current.rotation.x, rx, 7, dt);
      armR.current.rotation.z = damp(armR.current.rotation.z, rz, 7, dt);
    }

    // ตา: กะพริบ · ฟังแล้วตาโตขึ้น · คิดแล้วกลายเป็นเฟือง
    if (t > s.blinkAt) {
      s.blink = 1;
      s.blinkAt = t + 2.2 + Math.random() * 3;
    }
    s.blink = Math.max(0, s.blink - dt * 7);
    const open = 1 - Math.sin(Math.min(1, s.blink) * Math.PI) * 0.92;
    const big = listening ? 1.18 + s.lvl * 0.25 : talking ? 1.04 : 1;
    if (eyes.current) eyes.current.visible = !thinking;
    for (const e of [eyeL.current, eyeR.current]) if (e) e.scale.set(0.078 * big, 0.115 * big * open, 0.02);
    for (const g of [gearL.current, gearR.current]) {
      if (!g) continue;
      g.visible = thinking;
      g.rotation.z += dt * (g === gearL.current ? 3 : -3);
    }
    // ปาก
    if (smile.current) smile.current.visible = !talking && !thinking && !listening;
    if (flat.current) flat.current.visible = thinking;
    if (mouth.current) {
      mouth.current.visible = talking || listening;
      const h = talking ? 0.012 + s.amp * 0.085 : 0.03;
      const w = talking ? 0.08 + s.amp * 0.02 : 0.03;
      mouth.current.scale.set(w, h, 0.012);
    }
    // ไฟ/เรืองแสง
    const earI = listening ? 0.6 + s.lvl * 2.2 : 0;
    if (earMat.current) earMat.current.emissiveIntensity = damp(earMat.current.emissiveIntensity, earI, 10, dt);
    for (const g of [earGlowL.current, earGlowR.current]) {
      if (!g) continue;
      const m = g.material as THREE.SpriteMaterial;
      m.opacity = damp(m.opacity, listening ? 0.35 + s.lvl * 0.65 : 0, 10, dt);
      const k = 0.55 + (listening ? s.lvl * 0.5 + Math.sin(t * 6) * 0.04 : 0);
      g.scale.set(k, k, 1);
    }
    if (lampGlow.current) {
      const m = lampGlow.current.material as THREE.SpriteMaterial;
      m.opacity = 0.65 + Math.sin(t * 3) * 0.08 + (talking ? s.amp * 0.3 : 0);
    }
    if (eyeGlow.current) {
      const m = eyeGlow.current.material as THREE.SpriteMaterial;
      m.opacity = (thinking ? 0.32 + Math.sin(t * 8) * 0.08 : 0.26) + (talking ? s.amp * 0.25 : 0);
    }
  });

  const arm = (side: 1 | -1) => (
    <>
      <mesh position={[0, -0.16, 0]} material={M.white} castShadow>
        <capsuleGeometry args={[0.1, 0.18, 6, 16]} />
      </mesh>
      <mesh position={[0, -0.31, 0]} rotation={[Math.PI / 2, 0, 0]} material={M.dark}>
        <torusGeometry args={[0.095, 0.03, 8, 20]} />
      </mesh>
      <mesh position={[0, -0.36, 0]} material={M.orangeSoft}>
        <cylinderGeometry args={[0.12, 0.11, 0.09, 20]} />
      </mesh>
      <mesh position={[0, -0.47, 0.01]} scale={[1, 1.12, 0.88]} material={M.orangeSoft}>
        <sphereGeometry args={[0.13, 20, 16]} />
      </mesh>
      <mesh position={[side * 0.1, -0.44, 0.06]} rotation={[0, 0, side * 0.6]} material={M.orangeSoft}>
        <capsuleGeometry args={[0.04, 0.07, 4, 10]} />
      </mesh>
    </>
  );

  return (
    <group ref={root} position={position} scale={scale}>
      {/* ขา + รองเท้า */}
      {[-1, 1].map((sd) => (
        <group key={sd} position={[sd * 0.19, 0, 0]}>
          <mesh position={[0, 0.3, 0]} material={M.denim}>
            <cylinderGeometry args={[0.16, 0.15, 0.32, 20]} />
          </mesh>
          <mesh position={[0, 0.19, 0]} rotation={[Math.PI / 2, 0, 0]} material={M.denim}>
            <torusGeometry args={[0.155, 0.035, 8, 24]} />
          </mesh>
          <mesh position={[0, 0.1, 0.05]} scale={[1, 0.75, 1.3]} material={M.orange}>
            <sphereGeometry args={[0.16, 20, 14]} />
          </mesh>
          <mesh position={[0, 0.025, 0.05]} material={M.sole}>
            <boxGeometry args={[0.3, 0.05, 0.44]} />
          </mesh>
        </group>
      ))}

      <group ref={body}>
        {/* ลำตัว */}
        <mesh position={[0, 0.9, 0]} scale={[1, 1.04, 0.86]} material={M.white}>
          <sphereGeometry args={[0.42, 32, 24]} />
        </mesh>
        <mesh position={[0, 0.64, 0]} material={M.denim}>
          <cylinderGeometry args={[0.415, 0.4, 0.42, 32]} />
        </mesh>
        <mesh position={[0, 0.44, 0]} scale={[1, 0.45, 0.85]} material={M.denim}>
          <sphereGeometry args={[0.4, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2]} />
        </mesh>
        {/* เอี๊ยม + กระเป๋า + สาย + กระดุม */}
        <mesh position={[0, 0.93, 0.31]} rotation={[-0.12, 0, 0]} material={M.denim}>
          <boxGeometry args={[0.44, 0.34, 0.07]} />
        </mesh>
        <mesh position={[0, 0.9, 0.355]} rotation={[-0.12, 0, 0]} material={M.denim}>
          <boxGeometry args={[0.22, 0.14, 0.02]} />
        </mesh>
        {[-1, 1].map((sd) => (
          <group key={sd}>
            <mesh position={[sd * 0.17, 1.15, 0.2]} rotation={[-0.75, 0, sd * 0.1]} material={M.denim}>
              <boxGeometry args={[0.08, 0.32, 0.035]} />
            </mesh>
            <mesh position={[sd * 0.17, 1.06, 0.34]} rotation={[Math.PI / 2 - 0.12, 0, 0]} material={M.gold}>
              <cylinderGeometry args={[0.035, 0.035, 0.02, 14]} />
            </mesh>
          </group>
        ))}
        {/* เข็มขัดเครื่องมือ */}
        <mesh position={[0, 0.58, 0]} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.95, 1]} material={M.orangeSoft}>
          <torusGeometry args={[0.42, 0.045, 10, 40]} />
        </mesh>
        <mesh position={[0, 0.58, 0.44]} material={M.dark}>
          <boxGeometry args={[0.13, 0.1, 0.04]} />
        </mesh>
        {[-1, 1].map((sd) => (
          <mesh key={sd} position={[sd * 0.31, 0.51, 0.31]} rotation={[0, sd * 0.75, 0]} material={M.orangeSoft}>
            <boxGeometry args={[0.15, 0.17, 0.09]} />
          </mesh>
        ))}
        {/* ค้อน */}
        <group position={[-0.37, 0.52, 0.36]} rotation={[0.1, 0.5, 0.15]}>
          <mesh position={[0, -0.02, 0]} material={M.wood}>
            <cylinderGeometry args={[0.024, 0.024, 0.32, 10]} />
          </mesh>
          <mesh position={[0, 0.15, 0]} material={M.steel}>
            <boxGeometry args={[0.17, 0.055, 0.055]} />
          </mesh>
        </group>
        {/* ตลับเมตร */}
        <group position={[0.38, 0.55, 0.34]} rotation={[0, 0.75, 0]}>
          <mesh rotation={[Math.PI / 2, 0, 0]} material={M.orange}>
            <cylinderGeometry args={[0.075, 0.075, 0.06, 20]} />
          </mesh>
          <mesh position={[0, 0, 0.032]} rotation={[Math.PI / 2, 0, 0]} material={M.yellow}>
            <cylinderGeometry args={[0.04, 0.04, 0.01, 16]} />
          </mesh>
        </group>

        {/* แขน (หมุนที่หัวไหล่) */}
        <group ref={armL} position={[-0.45, 1.06, 0]}>
          {arm(-1)}
        </group>
        <group ref={armR} position={[0.45, 1.06, 0]}>
          {arm(1)}
        </group>

        {/* คอ + หัว (หมุนที่คอ) */}
        <mesh position={[0, 1.2, 0]} material={M.dark}>
          <cylinderGeometry args={[0.13, 0.15, 0.1, 20]} />
        </mesh>
        <group ref={head} position={[0, 1.18, 0]}>
          <mesh position={[0, 0.5, 0]} scale={[1.15, 0.93, 0.98]} material={M.white}>
            <sphereGeometry args={[0.6, 48, 36]} />
          </mesh>
          {/* จอหน้า */}
          <mesh position={[0, 0.43, 0.33]} scale={[1.08, 0.62, 0.62]} material={M.visor}>
            <sphereGeometry args={[0.5, 48, 32]} />
          </mesh>
          {glow && (
            <sprite ref={eyeGlow} position={[0, 0.46, 0.68]} scale={[0.95, 0.5, 1]}>
              <spriteMaterial map={glow} color="#3fd6ff" transparent opacity={0.26} depthWrite={false} blending={THREE.AdditiveBlending} />
            </sprite>
          )}
          <group ref={eyes}>
            <mesh ref={eyeL} position={[-0.2, 0.5, 0.607]} material={M.cyan} scale={[0.078, 0.115, 0.02]}>
              <sphereGeometry args={[1, 24, 16]} />
            </mesh>
            <mesh ref={eyeR} position={[0.2, 0.5, 0.607]} material={M.cyan} scale={[0.078, 0.115, 0.02]}>
              <sphereGeometry args={[1, 24, 16]} />
            </mesh>
          </group>
          <Gear gref={gearL} position={[-0.2, 0.5, 0.627]} />
          <Gear gref={gearR} position={[0.2, 0.5, 0.627]} />
          {/* ปาก: ยิ้ม (ว่าง) · วงรีเปิดตามเสียง (พูด/ฟัง) · เส้นตรง (คิด) */}
          <mesh ref={smile} position={[0, 0.375, 0.632]} rotation={[0, 0, Math.PI]} material={M.cyan}>
            <torusGeometry args={[0.065, 0.013, 8, 24, Math.PI]} />
          </mesh>
          <mesh ref={mouth} position={[0, 0.345, 0.63]} material={M.cyan} visible={false} scale={[0.08, 0.02, 0.012]}>
            <sphereGeometry args={[1, 20, 12]} />
          </mesh>
          <mesh ref={flat} position={[0.03, 0.35, 0.634]} rotation={[0, 0, 0.12]} material={M.cyan} visible={false}>
            <boxGeometry args={[0.1, 0.018, 0.01]} />
          </mesh>
          {/* หูฟัง (เรืองแสงตอนฟัง) */}
          {[-1, 1].map((sd) => (
            <group key={sd} position={[sd * 0.68, 0.47, -0.02]} rotation={[0, 0, Math.PI / 2]}>
              <mesh material={M.grey}>
                <cylinderGeometry args={[0.17, 0.17, 0.1, 28]} />
              </mesh>
              <mesh position={[0, sd * -0.055, 0]}>
                <cylinderGeometry args={[0.12, 0.12, 0.02, 24]} />
                <meshStandardMaterial
                  ref={sd === 1 ? earMat : undefined}
                  color="#ff7a1c"
                  emissive="#3fd6ff"
                  emissiveIntensity={0}
                  roughness={0.4}
                />
              </mesh>
              <mesh position={[0, sd * -0.06, 0]} rotation={[0, 0, 0]} material={M.orange}>
                <torusGeometry args={[0.15, 0.025, 8, 28]} />
              </mesh>
            </group>
          ))}
          {glow && (
            <>
              <sprite ref={earGlowL} position={[-0.78, 0.47, 0]} scale={[0.55, 0.55, 1]}>
                <spriteMaterial map={glow} color="#3fd6ff" transparent opacity={0} depthWrite={false} blending={THREE.AdditiveBlending} />
              </sprite>
              <sprite ref={earGlowR} position={[0.78, 0.47, 0]} scale={[0.55, 0.55, 1]}>
                <spriteMaterial map={glow} color="#3fd6ff" transparent opacity={0} depthWrite={false} blending={THREE.AdditiveBlending} />
              </sprite>
            </>
          )}
          {/* หมวกนิรภัย */}
          <group position={[0, 0.66, -0.02]}>
            <mesh scale={[1.14, 0.9, 1.08]} material={M.orange}>
              <sphereGeometry args={[0.62, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2]} />
            </mesh>
            <mesh position={[0, 0.0, 0.03]} scale={[1, 1, 1.0]} material={M.orange}>
              <cylinderGeometry args={[0.78, 0.8, 0.05, 48]} />
            </mesh>
            <mesh position={[0, 0.07, 0]} rotation={[Math.PI / 2, 0, 0]} scale={[1.13, 1.07, 1]} material={M.dark}>
              <torusGeometry args={[0.62, 0.03, 8, 48]} />
            </mesh>
            <mesh rotation={[0, Math.PI / 2, 0]} scale={[1.08, 0.9, 1.14]} material={M.orange}>
              <torusGeometry args={[0.6, 0.045, 10, 40, Math.PI]} />
            </mesh>
            {/* ไฟฉายคาดหัว */}
            <group position={[0, 0.3, 0.6]} rotation={[0.55, 0, 0]}>
              <mesh rotation={[Math.PI / 2, 0, 0]} material={M.dark}>
                <cylinderGeometry args={[0.11, 0.12, 0.1, 24]} />
              </mesh>
              <mesh position={[0, 0, 0.052]} rotation={[Math.PI / 2, 0, 0]} material={M.lens}>
                <cylinderGeometry args={[0.075, 0.075, 0.01, 24]} />
              </mesh>
              {glow && (
                <sprite ref={lampGlow} position={[0, 0, 0.1]} scale={[0.6, 0.6, 1]}>
                  <spriteMaterial map={glow} color="#ffd38a" transparent opacity={0.7} depthWrite={false} blending={THREE.AdditiveBlending} />
                </sprite>
              )}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
}
