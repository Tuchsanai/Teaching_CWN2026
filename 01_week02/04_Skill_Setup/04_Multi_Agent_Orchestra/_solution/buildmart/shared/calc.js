// shared/calc.js — เครื่องคำนวณวัสดุ (BUILDMART ข้อ 3.3) · ESM ล้วน ไม่มี dependency
// calculate(type, input) → { rows:[{sku, qty, unit, label}], extra? }
// ใช้ทั้งหน้า /calculator (B1) และ tag [CALC] ของ chat-worker (C2)

export const CALC_TYPES = ['concrete', 'wall', 'tile', 'paint', 'rebar'];

export const REBAR = {
  RB6: { sku: 'STL-001', kgPerM: 0.222, label: 'เหล็กเส้นกลม RB6 ยาว 10 ม.' },
  RB9: { sku: 'STL-002', kgPerM: 0.499, label: 'เหล็กเส้นกลม RB9 ยาว 10 ม.' },
  DB12: { sku: 'STL-003', kgPerM: 0.888, label: 'เหล็กข้ออ้อย DB12 ยาว 10 ม.' },
  DB16: { sku: 'STL-004', kgPerM: 1.578, label: 'เหล็กข้ออ้อย DB16 ยาว 10 ม.' },
};

/** ปัดขึ้นแบบกันเศษ floating point (เช่น 21.0000000001 → 21) */
export function ceilSafe(x) {
  return Math.ceil(Math.round(Number(x) * 1e6) / 1e6);
}

function num(v, def = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

function pick(input, ...keys) {
  for (const k of keys) if (input?.[k] !== undefined && input[k] !== null && input[k] !== '') return input[k];
  return undefined;
}

const row = (sku, qty, unit, label) => ({ sku, qty, unit, label });

export function calculate(type, input = {}) {
  const t = String(type || '').toLowerCase();
  switch (t) {
    case 'concrete': {
      const V = num(pick(input, 'volume', 'v'));
      return {
        rows: [
          row('CEM-001', ceilSafe(V * 7), 'ถุง', 'ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 (50 กก.)'),
          row('AGG-001', ceilSafe(V * 0.5), 'ลบ.ม.', 'ทรายหยาบ'),
          row('AGG-003', ceilSafe(V * 0.9), 'ลบ.ม.', 'หิน 3/4 (หินเบอร์ 1)'),
        ],
        extra: { volume: V, mix: '1:2:4' },
      };
    }
    case 'wall': {
      const A = num(pick(input, 'area', 'a'));
      const wt = String(pick(input, 'wallType', 'wall_type', 'brick') || 'brick').toLowerCase();
      const light = wt === 'light' || wt === 'aac' || wt === 'brk-002';
      return light
        ? {
            rows: [
              row('BRK-002', ceilSafe(A * 8.33), 'ก้อน', 'อิฐมวลเบา 7.5 ซม. (ก้อน)'),
              row('CEM-002', ceilSafe(A * 0.12), 'ถุง', 'ปูนก่อ สำเร็จรูป (50 กก.)'),
            ],
            extra: { area: A, wallType: 'light' },
          }
        : {
            rows: [
              row('BRK-001', ceilSafe(A * 140), 'ก้อน', 'อิฐมอญ (ก้อน)'),
              row('CEM-002', ceilSafe(A * 0.25), 'ถุง', 'ปูนก่อ สำเร็จรูป (50 กก.)'),
            ],
            extra: { area: A, wallType: 'brick' },
          };
    }
    case 'tile': {
      const A = num(pick(input, 'area', 'a'));
      return {
        rows: [
          row('TIL-001', ceilSafe((A * 1.1) / 1.44), 'กล่อง', 'กระเบื้องพื้น 60x60 ลายหินอ่อน (กล่อง 1.44 ตร.ม.)'),
          row('CEM-004', ceilSafe(A / 4), 'ถุง', 'ปูนกาวซีเมนต์ ปูกระเบื้อง (20 กก.)'),
          row('TIL-003', ceilSafe(A / 5), 'ถุง', 'ยาแนว สีเทา (1 กก.)'),
        ],
        extra: { area: A, waste: 0.1 },
      };
    }
    case 'paint': {
      const A = num(pick(input, 'area', 'a'));
      const N = num(pick(input, 'coats', 'n'), 2) || 2;
      const pt = String(pick(input, 'paintType', 'paint_type', 'kind') || 'interior').toLowerCase();
      const exterior = pt === 'exterior' || pt === 'outside' || pt === 'ภายนอก';
      return {
        rows: [
          exterior
            ? row('PNT-001', ceilSafe((A * N) / 30), 'แกลลอน', 'สีน้ำอะคริลิก ภายนอก สีขาว')
            : row('PNT-002', ceilSafe((A * N) / 30), 'แกลลอน', 'สีน้ำอะคริลิก ภายใน สีขาว'),
          row('PNT-003', ceilSafe(A / 40), 'แกลลอน', 'สีรองพื้นปูนใหม่'),
        ],
        extra: { area: A, coats: N, paintType: exterior ? 'exterior' : 'interior' },
      };
    }
    case 'rebar': {
      const size = String(pick(input, 'size', 'rebarSize', 'rebar_size') || 'DB12').toUpperCase();
      const spec = REBAR[size];
      if (!spec) throw new Error(`ไม่รู้จักขนาดเหล็ก ${size}`);
      const L = num(pick(input, 'length', 'l'));
      const bars = ceilSafe(L / 10);
      const weightKg = Math.round(L * spec.kgPerM * 100) / 100;
      return { rows: [row(spec.sku, bars, 'เส้น', spec.label)], bars, weightKg, extra: { size, length: L, bars, weightKg } };
    }
    default:
      throw new Error(`ไม่รู้จักประเภทการคำนวณ ${type}`);
  }
}
