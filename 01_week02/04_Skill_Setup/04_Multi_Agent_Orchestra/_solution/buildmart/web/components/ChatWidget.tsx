'use client';
// components/ChatWidget.tsx — แชทบอท "น้องช่าง" ลอยมุมขวาล่างทุกหน้า (C1 · v3: มาสคอต 3D + คุยด้วยเสียง)
// - ส่งคำถาม POST /api/chat → อ่าน SSE: queued → status → delta (ข้อความสะสม) → done | error
//   (v3: done มี retrieved + products → แสดงชิปสินค้า 📦 ลิงก์ไปหน้าสินค้า)
// - ประวัติ: GET /api/chat/history ตอนเปิดครั้งแรก
// - อ่านออกเสียง: GET /api/tts/status → ปุ่ม 🔊 (tts-play) + สวิตช์ tts-auto · POST /api/tts → <audio data-testid="chat-audio">
// - v3 เสียงเข้า: GET /api/voice/status → ปุ่มไมค์ voice-mic (กดเริ่ม/กดหยุด · MediaRecorder · มีแถบระดับเสียง)
//   → POST /api/voice (multipart audio) → ข้อความ → ฟองผู้ใช้ป้าย 🎙 (chat-msg-voice) → ส่งเข้าแชทตามปกติ
//   · input ซ่อน voice-file (ส่งไฟล์เสียงตรง ๆ) · สวิตช์ voice-mode "คุยด้วยเสียง" = ตอบเสร็จเล่นเสียงอัตโนมัติ
// - v3 มาสคอต: <Mascot data-testid="mascot" data-state=idle|listening|thinking|talking data-mouth=0..1>
//   ปากขยับตามความดังเสียงจริงจาก WebAudio AnalyserNode ที่ต่อกับ <audio data-testid="chat-audio">
// - บอทใส่ตะกร้า → done.cartCount → window event 'bm:cart' ให้ Header อัปเดตตัวเลข
// - เปิดแผงจากที่อื่น: window.dispatchEvent(new CustomEvent('bm:chat-open', {detail:{voice:true}}))
// - e2e: window.__bmAudio = {audioId, startedAt, durationMs} และ window.__bmAudioLog (array)
import { Fragment, useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { ProductImage } from './CatImage';
import Mascot from './three/Mascot';
import type { Live, MascotState } from './three/util';
import './ChatWidget.css';

type Cite = { filename: string; page: number; snippet?: string };
type Phase = 'queued' | 'thinking' | 'streaming' | 'done' | 'error';
type Msg = {
  key: string;
  role: 'user' | 'bot';
  text: string;
  phase: Phase;
  voice?: boolean;
  cites?: Cite[];
  products?: string[];
  quoteNo?: string;
  audioId?: string;
  durationMs?: number;
  ttsLoading?: boolean;
  ttsError?: boolean;
};
type RecState = 'idle' | 'starting' | 'recording' | 'transcribing';

const SUGGESTIONS = ['ร้านเปิดกี่โมง', 'เทคอนกรีต 3 คิวใช้ปูนกี่ถุง', 'ปูนเก็บได้นานแค่ไหน'];
const AUTO_KEY = 'bm_tts_auto';
const VOICE_KEY = 'bm_voice_mode';
const MAX_REC_MS = 30_000;
const METER_BARS = 14;

declare global {
  interface Window {
    __bmAudio?: { audioId: string; startedAt: number; durationMs: number | null };
    __bmAudioLog?: { audioId: string; startedAt: number; durationMs: number | null }[];
    webkitAudioContext?: typeof AudioContext;
  }
}

let seq = 0;
const newKey = () => `m${Date.now().toString(36)}${(seq++).toString(36)}`;

/** ตัด tag ภายในและเลขอ้างอิง [n] ที่อาจหลุดมาระหว่าง stream */
function clean(t: string): string {
  return t
    .replace(/\[(CALC|ADD_TO_CART|QUOTE)\][^\n]*/g, '')
    .replace(/\s?\[\d+\]/g, '')
    .replace(/<think>[\s\S]*?(<\/think>|$)/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

/** **ตัวหนา** → <strong> (React escape HTML ให้เอง ไม่ใช้ innerHTML) */
function inline(s: string, k: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /\*\*(.+?)\*\*/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let i = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(s.slice(last, m.index));
    out.push(<strong key={`${k}b${i++}`}>{m[1]}</strong>);
    last = m.index + m[0].length;
  }
  if (last < s.length) out.push(s.slice(last));
  return out;
}

/** markdown อย่างง่าย: ย่อหน้า/ขึ้นบรรทัด · ตัวหนา · รายการ - • * และ 1. */
function Markdown({ text }: { text: string }) {
  const lines = text.split('\n');
  const blocks: ReactNode[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;
  let para: string[] = [];
  const flushPara = () => {
    if (!para.length) return;
    const k = `p${blocks.length}`;
    blocks.push(
      <p key={k}>
        {para.map((l, i) => (
          <Fragment key={i}>
            {i > 0 && <br />}
            {inline(l, `${k}-${i}`)}
          </Fragment>
        ))}
      </p>,
    );
    para = [];
  };
  const flushList = () => {
    if (!list) return;
    const k = `l${blocks.length}`;
    const items = list.items.map((it, i) => <li key={i}>{inline(it, `${k}-${i}`)}</li>);
    blocks.push(list.ordered ? <ol key={k}>{items}</ol> : <ul key={k}>{items}</ul>);
    list = null;
  };
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '');
    const ul = /^\s*[-*•]\s+(.*)$/.exec(line);
    const ol = /^\s*\d+[.)]\s+(.*)$/.exec(line);
    if (ul || ol) {
      flushPara();
      const ordered = !!ol;
      if (!list || list.ordered !== ordered) {
        flushList();
        list = { ordered, items: [] };
      }
      list.items.push((ul || ol)![1]);
    } else if (!line.trim()) {
      flushPara();
      flushList();
    } else {
      flushList();
      para.push(line.replace(/^#{1,6}\s+/, ''));
    }
  }
  flushPara();
  flushList();
  return <>{blocks}</>;
}

function uniqCites(c?: Cite[]): Cite[] {
  const seen = new Set<string>();
  return (c || []).filter((x) => {
    if (!x?.filename) return false;
    const k = `${x.filename}#${x.page}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function skuList(p: unknown): string[] {
  if (!Array.isArray(p)) return [];
  const out: string[] = [];
  for (const x of p) {
    const s = typeof x === 'string' ? x : x && typeof x === 'object' && 'sku' in x ? String((x as any).sku) : '';
    if (s && !out.includes(s)) out.push(s);
  }
  return out.slice(0, 4);
}

function rms(an: AnalyserNode, buf: Float32Array<ArrayBuffer>): number {
  an.getFloatTimeDomainData(buf);
  let s = 0;
  for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i];
  return Math.sqrt(s / buf.length);
}

function pickMime(): string {
  if (typeof MediaRecorder === 'undefined') return '';
  for (const m of ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4']) {
    try {
      if (MediaRecorder.isTypeSupported(m)) return m;
    } catch {
      /* ignore */
    }
  }
  return '';
}

function Switch({ testId, checked, onChange, label, title }: { testId: string; checked: boolean; onChange: (v: boolean) => void; label: string; title: string }) {
  return (
    <label className="bmchat-switch" title={title}>
      <input type="checkbox" data-testid={testId} checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="bmchat-switch-track" aria-hidden>
        <span className="bmchat-switch-knob" />
      </span>
      <span className="bmchat-switch-text">{label}</span>
    </label>
  );
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [ttsOn, setTtsOn] = useState(false);
  const [auto, setAuto] = useState(false);
  const [voiceOn, setVoiceOn] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const [rec, setRec] = useState<RecState>('idle');
  const [recMs, setRecMs] = useState(0);
  const [voiceNote, setVoiceNote] = useState('');
  const [playingKey, setPlayingKey] = useState<string | null>(null);
  const historyLoaded = useRef(false);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const msgsRef = useRef<Msg[]>([]);
  const autoRef = useRef(false);
  const ttsRef = useRef(false);
  const voiceModeRef = useRef(false);
  msgsRef.current = msgs;
  autoRef.current = auto;
  ttsRef.current = ttsOn;
  voiceModeRef.current = voiceMode;

  // ---------- เสียง: WebAudio (ความดังเสียงพูด → ปากมาสคอต · ไมค์ → แถบระดับ) ----------
  const ampRef = useRef<Live>({ current: 0 }).current;
  const levelRef = useRef<Live>({ current: 0 }).current;
  const ctxRef = useRef<AudioContext | null>(null);
  const playAnRef = useRef<AnalyserNode | null>(null);
  const micAnRef = useRef<AnalyserNode | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recStartRef = useRef(0);
  const recTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const meterRef = useRef<HTMLDivElement>(null);
  const streamingRef = useRef(false);
  const playingRef = useRef(false);

  const getCtx = useCallback((): AudioContext | null => {
    if (ctxRef.current) return ctxRef.current;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    try {
      ctxRef.current = new AC();
    } catch {
      return null;
    }
    return ctxRef.current;
  }, []);

  /** ต่อ <audio> เข้า AnalyserNode (ทำได้ครั้งเดียวต่อ element · ต่อเฉพาะตอน context running ไม่งั้นเสียงจะเงียบ) */
  const ensurePlaybackGraph = useCallback(async () => {
    if (playAnRef.current) return;
    const a = audioRef.current;
    const ctx = getCtx();
    if (!a || !ctx) return;
    try {
      if (ctx.state !== 'running') await Promise.race([ctx.resume(), new Promise((r) => setTimeout(r, 300))]);
      if (ctx.state !== 'running' || playAnRef.current) return;
      const src = ctx.createMediaElementSource(a);
      const an = ctx.createAnalyser();
      an.fftSize = 1024;
      an.smoothingTimeConstant = 0.5;
      src.connect(an);
      an.connect(ctx.destination);
      playAnRef.current = an;
    } catch (e) {
      console.warn('[chat] analyser ใช้ไม่ได้ ใช้ปากจำลองแทน', e);
    }
  }, [getCtx]);

  // ลูปเฟรม: คำนวณความดังทุกเฟรมขณะเปิดแผงหรือกำลังเล่นเสียง
  useEffect(() => {
    if (!open && !playingKey && rec === 'idle') {
      ampRef.current = 0;
      return;
    }
    let raf = 0;
    const buf = new Float32Array(new ArrayBuffer(4096));
    const bars = () => Array.from(meterRef.current?.children || []) as HTMLElement[];
    const tick = (now: number) => {
      const t = now / 1000;
      // พูด
      let amp = 0;
      if (playingRef.current) {
        const an = playAnRef.current;
        if (an) amp = Math.min(1, Math.max(0, (rms(an, buf) - 0.01) * 5.5));
        else amp = 0.25 + 0.45 * Math.abs(Math.sin(t * 13)) * (0.6 + 0.4 * Math.sin(t * 3.1));
      } else if (streamingRef.current) {
        amp = 0.15 + 0.3 * Math.abs(Math.sin(t * 15)) * (0.5 + 0.5 * Math.sin(t * 2.3));
      }
      ampRef.current = amp;
      // ไมค์
      const man = micAnRef.current;
      let lvl = 0;
      if (man) {
        lvl = Math.min(1, rms(man, buf) * 9);
      }
      levelRef.current = lvl;
      if (man) {
        const bs = bars();
        bs.forEach((b, i) => {
          const wob = 0.55 + 0.45 * Math.sin(t * 9 + i * 0.9);
          const v = Math.max(0.08, Math.min(1, lvl * wob * (1.3 - Math.abs(i - bs.length / 2) / bs.length)));
          b.style.transform = `scaleY(${v.toFixed(3)})`;
        });
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [open, playingKey, rec, ampRef, levelRef]);

  const patch = useCallback((key: string, p: Partial<Msg>) => {
    setMsgs((cur) => cur.map((m) => (m.key === key ? { ...m, ...p } : m)));
  }, []);

  // ---------- เริ่มต้น ----------
  useEffect(() => {
    if (!window.__bmAudioLog) window.__bmAudioLog = [];
    try {
      setAuto(localStorage.getItem(AUTO_KEY) === '1');
      setVoiceMode(localStorage.getItem(VOICE_KEY) === '1');
    } catch {
      /* ignore */
    }
  }, []);

  const refreshTts = useCallback(async () => {
    try {
      const r = await fetch('/api/tts/status', { cache: 'no-store' });
      const j = await r.json();
      setTtsOn(!!j.enabled);
    } catch {
      setTtsOn(false);
    }
  }, []);

  const refreshVoice = useCallback(async () => {
    try {
      const r = await fetch('/api/voice/status', { cache: 'no-store' });
      if (!r.ok) throw new Error(String(r.status));
      const j = await r.json();
      setVoiceOn(!!j.enabled && typeof window !== 'undefined' && !!navigator.mediaDevices?.getUserMedia);
    } catch {
      setVoiceOn(false);
    }
  }, []);

  useEffect(() => {
    refreshTts();
    refreshVoice();
  }, [refreshTts, refreshVoice]);

  useEffect(() => {
    if (!open) return;
    refreshTts();
    refreshVoice();
    setTimeout(() => inputRef.current?.focus(), 50);
    if (historyLoaded.current) return;
    historyLoaded.current = true;
    (async () => {
      try {
        const r = await fetch('/api/chat/history', { cache: 'no-store' });
        const j = await r.json();
        const hist: Msg[] = (j.messages || []).map((m: any) => ({
          key: `h${m.id}`,
          role: m.role === 'user' ? 'user' : 'bot',
          text: m.role === 'user' ? String(m.content) : clean(String(m.content)),
          phase: 'done' as Phase,
          cites: m.cites || [],
        }));
        if (hist.length) setMsgs((cur) => [...hist, ...cur]);
      } catch {
        /* ไม่มีประวัติก็ไม่เป็นไร */
      }
    })();
  }, [open, refreshTts, refreshVoice]);

  // เปิดแผงจากปุ่มในหน้าอื่น (เช่น หน้าแรก "คุยกับน้องช่าง")
  useEffect(() => {
    const on = (e: Event) => {
      setOpen(true);
      if ((e as CustomEvent).detail?.voice) getCtx()?.resume().catch(() => {});
    };
    window.addEventListener('bm:chat-open', on);
    return () => window.removeEventListener('bm:chat-open', on);
  }, [getCtx]);

  // เลื่อนลงล่างสุดเมื่อมีข้อความใหม่
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [msgs, open, rec, voiceNote]);

  // ---------- เสียงพูด (TTS) ----------
  const playAudio = useCallback(
    async (key: string, audioId: string, durationMs: number | null) => {
      const a = audioRef.current;
      if (!a) return;
      a.pause();
      await ensurePlaybackGraph();
      a.src = `/api/tts/${audioId}`;
      a.dataset.audioId = audioId;
      setPlayingKey(key);
      const rec = { audioId, startedAt: performance.now(), durationMs };
      try {
        await a.play();
        rec.startedAt = performance.now();
      } catch (e) {
        console.warn('[chat] audio.play() ถูกบล็อก', e);
      }
      window.__bmAudio = rec;
      (window.__bmAudioLog ||= []).push(rec);
    },
    [ensurePlaybackGraph],
  );

  const speak = useCallback(
    async (key: string) => {
      const m = msgsRef.current.find((x) => x.key === key);
      if (!m || m.ttsLoading) return;
      if (m.audioId) return playAudio(key, m.audioId, m.durationMs ?? null);
      patch(key, { ttsLoading: true, ttsError: false });
      try {
        const r = await fetch('/api/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: m.text }),
        });
        const j = await r.json();
        if (!r.ok || !j.audioId) throw new Error(j.error || `HTTP ${r.status}`);
        patch(key, { ttsLoading: false, audioId: j.audioId, durationMs: j.durationMs ?? undefined });
        await playAudio(key, j.audioId, j.durationMs ?? null);
      } catch (e) {
        console.warn('[chat] tts error', e);
        patch(key, { ttsLoading: false, ttsError: true });
      }
    },
    [patch, playAudio],
  );

  // ---------- ส่งคำถาม ----------
  const send = useCallback(
    async (raw: string, opts?: { voice?: boolean }) => {
      const text = raw.trim();
      if (!text || busy) return;
      setBusy(true);
      setVoiceNote('');
      if (!opts?.voice) setInput('');
      // กดส่ง = user gesture → ปลดล็อก AudioContext ไว้ให้เล่นเสียงตอบอัตโนมัติ
      if (voiceModeRef.current || autoRef.current) getCtx()?.resume().catch(() => {});
      const botKey = newKey();
      setMsgs((cur) => [
        ...cur,
        { key: newKey(), role: 'user', text, phase: 'done', voice: !!opts?.voice },
        { key: botKey, role: 'bot', text: '', phase: 'queued' },
      ]);
      let finished = false;
      const fail = (msg: string) => {
        finished = true;
        streamingRef.current = false;
        patch(botKey, { phase: 'error', text: msg });
      };
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
          body: JSON.stringify({ text }),
        });
        if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
        const reader = res.body.getReader();
        const dec = new TextDecoder();
        let buf = '';
        const handle = (event: string, data: any) => {
          switch (event) {
            case 'queued':
              patch(botKey, { phase: 'queued' });
              break;
            case 'status':
              setMsgs((cur) =>
                cur.map((m) => (m.key === botKey && m.phase === 'queued' ? { ...m, phase: 'thinking' } : m)),
              );
              break;
            case 'delta':
              streamingRef.current = true;
              patch(botKey, { phase: 'streaming', text: clean(String(data?.text ?? '')) });
              break;
            case 'done': {
              finished = true;
              streamingRef.current = false;
              const finalText = clean(String(data?.text ?? '')) || 'ขออภัยครับ ไม่ได้รับคำตอบ';
              patch(botKey, {
                phase: 'done',
                text: finalText,
                cites: uniqCites(data?.cites),
                products: skuList(data?.products),
                quoteNo: data?.quoteNo || undefined,
              });
              if (typeof data?.cartCount === 'number') {
                window.dispatchEvent(new CustomEvent('bm:cart', { detail: { count: data.cartCount } }));
              }
              if ((autoRef.current || voiceModeRef.current) && ttsRef.current) {
                // รอให้ state อัปเดตก่อน แล้วค่อยสร้างเสียง
                setTimeout(() => speak(botKey), 0);
              }
              break;
            }
            case 'error':
              fail(
                data?.error === 'timeout'
                  ? 'ขออภัยครับ ระบบตอบช้ากว่าปกติ (เกิน 4 นาที) ลองถามใหม่อีกครั้งนะครับ'
                  : 'ขออภัยครับ ระบบแชทขัดข้องชั่วคราว ลองใหม่อีกครั้งนะครับ',
              );
              break;
          }
        };
        for (;;) {
          const { value, done } = await reader.read();
          if (done) break;
          buf += dec.decode(value, { stream: true }).replace(/\r\n/g, '\n');
          let idx: number;
          while ((idx = buf.indexOf('\n\n')) >= 0) {
            const block = buf.slice(0, idx);
            buf = buf.slice(idx + 2);
            let event = 'message';
            const data: string[] = [];
            for (const line of block.split('\n')) {
              if (line.startsWith(':')) continue;
              if (line.startsWith('event:')) event = line.slice(6).trim();
              else if (line.startsWith('data:')) data.push(line.slice(5).trimStart());
            }
            if (!data.length) continue;
            let parsed: any = null;
            try {
              parsed = JSON.parse(data.join('\n'));
            } catch {
              parsed = { text: data.join('\n') };
            }
            handle(event, parsed);
          }
        }
        if (!finished) fail('ขออภัยครับ การเชื่อมต่อขาดหาย ลองใหม่อีกครั้งนะครับ');
      } catch (e) {
        console.warn('[chat] error', e);
        if (!finished) fail('ขออภัยครับ เชื่อมต่อระบบแชทไม่ได้ ลองใหม่อีกครั้งนะครับ');
      } finally {
        streamingRef.current = false;
        setBusy(false);
        setTimeout(() => inputRef.current?.focus(), 0);
      }
    },
    [busy, patch, speak, getCtx],
  );

  // ---------- เสียงเข้า (ไมค์ → /api/voice → แชท) ----------
  const transcribe = useCallback(
    async (blob: Blob, filename: string) => {
      setRec('transcribing');
      try {
        const fd = new FormData();
        fd.append('audio', blob, filename);
        const r = await fetch('/api/voice', { method: 'POST', body: fd });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
        const text = String(j.text || '').trim();
        setRec('idle');
        if (!text) {
          setVoiceNote('ไม่ได้ยินชัด ๆ ครับ ลองพูดอีกครั้งใกล้ไมค์หน่อยนะครับ');
          return;
        }
        await send(text, { voice: true });
      } catch (e) {
        console.warn('[chat] voice error', e);
        setRec('idle');
        setVoiceNote('ถอดเสียงไม่สำเร็จ ลองใหม่อีกครั้ง หรือพิมพ์คำถามแทนได้ครับ');
      }
    },
    [send],
  );

  const cleanupMic = useCallback(() => {
    if (recTimer.current) clearTimeout(recTimer.current);
    recTimer.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    micAnRef.current = null;
    levelRef.current = 0;
  }, [levelRef]);

  const stopRec = useCallback(() => {
    const r = recorderRef.current;
    if (r && r.state !== 'inactive') r.stop();
  }, []);

  const startRec = useCallback(async () => {
    if (busy || rec !== 'idle') return;
    setVoiceNote('');
    setRec('starting');
    const ctx = getCtx();
    ctx?.resume().catch(() => {});
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 },
      });
      streamRef.current = stream;
      const mime = pickMime();
      const mr = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      recorderRef.current = mr;
      chunksRef.current = [];
      mr.ondataavailable = (e) => {
        if (e.data && e.data.size) chunksRef.current.push(e.data);
      };
      mr.onstop = () => {
        const type = mr.mimeType || mime || 'audio/webm';
        const blob = new Blob(chunksRef.current, { type });
        const dur = performance.now() - recStartRef.current;
        cleanupMic();
        recorderRef.current = null;
        if (blob.size < 800 || dur < 300) {
          setRec('idle');
          setVoiceNote('สั้นไปนิดครับ กดไมค์แล้วพูดคำถาม จากนั้นกดอีกครั้งเพื่อส่ง');
          return;
        }
        const ext = type.includes('ogg') ? 'ogg' : type.includes('mp4') ? 'm4a' : 'webm';
        transcribe(blob, `voice.${ext}`);
      };
      if (ctx) {
        try {
          const src = ctx.createMediaStreamSource(stream);
          const an = ctx.createAnalyser();
          an.fftSize = 1024;
          src.connect(an);
          micAnRef.current = an;
        } catch {
          /* ไม่มีแถบระดับเสียงก็อัดได้ */
        }
      }
      mr.start(250);
      recStartRef.current = performance.now();
      setRecMs(0);
      setRec('recording');
      recTimer.current = setTimeout(stopRec, MAX_REC_MS);
    } catch (e: any) {
      console.warn('[chat] mic error', e);
      cleanupMic();
      setRec('idle');
      setVoiceNote(
        e?.name === 'NotAllowedError'
          ? 'เบราว์เซอร์ไม่อนุญาตให้ใช้ไมค์ครับ กดอนุญาตที่แถบที่อยู่แล้วลองใหม่'
          : 'เปิดไมค์ไม่ได้ครับ ลองตรวจอุปกรณ์ หรือพิมพ์คำถามแทนได้',
      );
    }
  }, [busy, rec, getCtx, cleanupMic, stopRec, transcribe]);

  // ตัวจับเวลาที่แสดงขณะอัด
  useEffect(() => {
    if (rec !== 'recording') return;
    const id = setInterval(() => setRecMs(performance.now() - recStartRef.current), 200);
    return () => clearInterval(id);
  }, [rec]);

  // ปิดแผง/ออกจากหน้า → หยุดไมค์
  useEffect(() => {
    if (!open && recorderRef.current) {
      recorderRef.current.onstop = null;
      stopRec();
      cleanupMic();
      setRec('idle');
    }
  }, [open, stopRec, cleanupMic]);
  useEffect(() => () => cleanupMic(), [cleanupMic]);

  const toggleMic = () => {
    if (rec === 'recording') stopRec();
    else if (rec === 'idle') startRec();
  };

  const onVoiceFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (!f || busy || rec !== 'idle') return;
    transcribe(f, f.name || 'voice.wav');
  };

  const toggleAuto = (v: boolean) => {
    setAuto(v);
    try {
      localStorage.setItem(AUTO_KEY, v ? '1' : '0');
    } catch {
      /* ignore */
    }
  };
  const toggleVoiceMode = (v: boolean) => {
    setVoiceMode(v);
    if (v) getCtx()?.resume().catch(() => {});
    try {
      localStorage.setItem(VOICE_KEY, v ? '1' : '0');
    } catch {
      /* ignore */
    }
  };

  // ---------- สถานะมาสคอต ----------
  const last = msgs[msgs.length - 1];
  const waiting = busy && last?.role === 'bot' && (last.phase === 'queued' || last.phase === 'thinking');
  const mascotState: MascotState =
    rec === 'recording' || rec === 'starting'
      ? 'listening'
      : rec === 'transcribing' || waiting
        ? 'thinking'
        : playingKey || (busy && last?.phase === 'streaming')
          ? 'talking'
          : 'idle';
  playingRef.current = !!playingKey;
  const mood =
    mascotState === 'listening'
      ? 'กำลังฟังอยู่ครับ… พูดได้เลย'
      : rec === 'transcribing'
        ? 'กำลังถอดเสียงที่พูด…'
        : mascotState === 'thinking'
          ? 'กำลังค้นข้อมูลให้ครับ…'
          : playingKey
            ? 'กำลังพูด… 🔊'
            : busy
              ? 'กำลังตอบ…'
              : 'ผู้ช่วยเรื่องวัสดุก่อสร้าง · ตอบทันที 24 ชม.';
  const secs = Math.floor(recMs / 1000);

  // ---------- UI ----------
  return (
    <div className="bmchat no-print">
      {!open && (
        <button
          type="button"
          className="bmchat-fab"
          data-testid="chat-open"
          aria-label="เปิดแชทกับน้องช่าง"
          onClick={() => setOpen(true)}
        >
          <span className="bmchat-fab-icon" aria-hidden>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/mascot.webp" alt="" onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')} />
            <i>💬</i>
          </span>
          <span className="bmchat-fab-label">ถามน้องช่าง</span>
        </button>
      )}

      {open && (
        <section
          className={`bmchat-panel state-${mascotState}`}
          data-testid="chat-panel"
          data-lipsync={playAnRef.current ? "analyser" : "synthetic"}
          role="dialog"
          aria-label="แชทกับน้องช่าง"
        >
          <header className="bmchat-head">
            <div className="bmchat-stage">
              <Mascot state={mascotState} ampRef={ampRef} levelRef={levelRef} />
            </div>
            <div className="bmchat-title">
              <b>น้องช่าง 🤖 BuildMart</b>
              <span className="bmchat-mood">
                <i className={`bmchat-led ${mascotState}`} aria-hidden />
                {mood}
              </span>
            </div>
            <button type="button" className="bmchat-close" aria-label="ปิดแชท" data-testid="chat-close" onClick={() => setOpen(false)}>
              ✕
            </button>
            {(ttsOn || voiceOn) && (
              <div className="bmchat-toggles">
                {(voiceOn || ttsOn) && (
                  <Switch
                    testId="voice-mode"
                    checked={voiceMode}
                    onChange={toggleVoiceMode}
                    label="คุยด้วยเสียง"
                    title="ตอบเสร็จแล้วน้องช่างพูดคำตอบให้ฟังอัตโนมัติ"
                  />
                )}
                {ttsOn && (
                  <Switch testId="tts-auto" checked={auto} onChange={toggleAuto} label="อ่านออกเสียงอัตโนมัติ" title="อ่านออกเสียงคำตอบอัตโนมัติ" />
                )}
              </div>
            )}
          </header>

          <div className="bmchat-list" ref={listRef} aria-live="polite">
            <div className="bmchat-welcome">
              สวัสดีครับ ผม <b>น้องช่าง</b> 👷 ถามได้ทั้งราคา สต็อก 3 สาขา คำนวณวัสดุ ใส่ตะกร้า หรือขอใบเสนอราคาครับ
              {voiceOn && <> · กด 🎙 แล้วพูดถามได้เลย</>}
            </div>
            {msgs.map((m) =>
              m.role === 'user' ? (
                m.voice ? (
                  <div key={m.key} className="bmchat-row user voice" data-testid="chat-msg-voice">
                    <span className="bmchat-voice-badge" aria-label="ถามด้วยเสียง">
                      🎙 เสียง
                    </span>
                    <div className="bmchat-bubble user" data-testid="chat-msg-user">
                      {m.text}
                    </div>
                  </div>
                ) : (
                  <div key={m.key} className="bmchat-row user">
                    <div className="bmchat-bubble user" data-testid="chat-msg-user">
                      {m.text}
                    </div>
                  </div>
                )
              ) : (
                <div key={m.key} className="bmchat-row bot">
                  {(m.phase === 'queued' || m.phase === 'thinking') && (
                    <div className={`bmchat-status ${m.phase}`} data-testid="chat-status">
                      <span className="bmchat-dots" aria-hidden>
                        <i />
                        <i />
                        <i />
                      </span>
                      {m.phase === 'queued' ? 'รอคิว…' : 'กำลังคิด…'}
                    </div>
                  )}
                  {(m.text || m.phase === 'done') && (
                    <div
                      className={`bmchat-bubble bot${m.phase === 'error' ? ' error' : ''}${playingKey === m.key ? ' speaking' : ''}`}
                      data-testid="chat-msg-bot"
                      data-done={m.phase === 'done' || m.phase === 'error' ? 'true' : 'false'}
                    >
                      <Markdown text={m.text} />
                      {m.phase === 'streaming' && <span className="bmchat-caret" aria-hidden />}
                    </div>
                  )}
                  {m.phase === 'done' && (m.cites?.length || m.quoteNo || m.products?.length || ttsOn) ? (
                    <div className="bmchat-meta">
                      {m.cites?.map((c) => (
                        <a
                          key={`${c.filename}#${c.page}`}
                          className="bmchat-cite"
                          data-testid="chat-cite"
                          href={`/api/docs/${encodeURIComponent(c.filename)}#page=${c.page}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          title={c.snippet || `${c.filename} หน้า ${c.page}`}
                        >
                          📄 {c.filename} · หน้า {c.page}
                        </a>
                      ))}
                      {m.products?.map((sku) => (
                        <a key={sku} className="bmchat-cite product" data-testid="chat-product" href={`/products/${encodeURIComponent(sku)}`}>
                          <span className="bmchat-pimg" aria-hidden>
                            <ProductImage sku={sku} className="bmchat-pimg-img" />
                          </span>
                          {sku}
                        </a>
                      ))}
                      {m.quoteNo && (
                        <a className="bmchat-cite quote" href={`/quote/${encodeURIComponent(m.quoteNo)}`}>
                          🧾 {m.quoteNo}
                        </a>
                      )}
                      {ttsOn && (
                        <button
                          type="button"
                          className={`bmchat-tts${m.ttsLoading ? ' loading' : ''}${playingKey === m.key ? ' active' : ''}`}
                          data-testid="tts-play"
                          data-loading={m.ttsLoading ? 'true' : 'false'}
                          aria-busy={m.ttsLoading ? true : undefined}
                          disabled={m.ttsLoading}
                          onClick={() => speak(m.key)}
                          title={m.ttsError ? 'สร้างเสียงไม่สำเร็จ ลองอีกครั้ง' : 'ฟังคำตอบนี้'}
                        >
                          {m.ttsLoading ? (
                            <span className="bmchat-spin" aria-hidden />
                          ) : playingKey === m.key ? (
                            <span className="bmchat-eq" aria-hidden>
                              <i />
                              <i />
                              <i />
                            </span>
                          ) : (
                            <span aria-hidden>🔊</span>
                          )}
                          {m.ttsLoading ? 'กำลังสร้างเสียง…' : m.ttsError ? 'ลองอีกครั้ง' : 'ฟัง'}
                        </button>
                      )}
                    </div>
                  ) : null}
                </div>
              ),
            )}
            {rec === 'transcribing' && (
              <div className="bmchat-row user voice pending" data-testid="voice-transcribing">
                <div className="bmchat-bubble user ghost">
                  <span className="bmchat-dots" aria-hidden>
                    <i />
                    <i />
                    <i />
                  </span>{' '}
                  🎙 กำลังถอดเสียง…
                </div>
              </div>
            )}
            {voiceNote && (
              <div className="bmchat-note" data-testid="voice-note" role="status">
                {voiceNote}
              </div>
            )}
          </div>

          <div className="bmchat-suggest">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" data-testid="chat-suggest" disabled={busy} onClick={() => send(s)}>
                {s}
              </button>
            ))}
          </div>

          <form
            className={`bmchat-form${rec === 'recording' ? ' recording' : ''}`}
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            {voiceOn && (
              <button
                type="button"
                className={`bmchat-mic ${rec}`}
                data-testid="voice-mic"
                data-recording={rec === 'recording' ? 'true' : 'false'}
                aria-pressed={rec === 'recording'}
                aria-label={rec === 'recording' ? 'หยุดอัดและส่งคำถาม' : 'กดแล้วพูดถาม'}
                title={rec === 'recording' ? 'กดอีกครั้งเพื่อส่ง' : 'กดแล้วพูดถาม'}
                disabled={(busy && rec !== 'recording') || rec === 'transcribing' || rec === 'starting'}
                onClick={toggleMic}
              >
                {rec === 'recording' ? <span className="bmchat-stop" aria-hidden /> : rec === 'transcribing' ? <span className="bmchat-spin" aria-hidden /> : <MicIcon />}
              </button>
            )}
            <div className="bmchat-inputwrap">
              <textarea
                ref={inputRef}
                className="bmchat-input"
                data-testid="chat-input"
                rows={1}
                placeholder={voiceOn ? 'พิมพ์คำถาม หรือกด 🎙 แล้วพูด' : 'พิมพ์คำถาม เช่น ปูนซีเมนต์ถุงละเท่าไร'}
                value={input}
                maxLength={2000}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    send(input);
                  }
                }}
              />
              {rec === 'recording' && (
                <div className="bmchat-recording" data-testid="voice-level" aria-live="polite">
                  <span className="bmchat-recdot" aria-hidden />
                  <span className="bmchat-rectime">
                    0:{String(secs).padStart(2, '0')}
                  </span>
                  <div className="bmchat-meter" ref={meterRef} aria-hidden>
                    {Array.from({ length: METER_BARS }, (_, i) => (
                      <i key={i} />
                    ))}
                  </div>
                  <span className="bmchat-rechint">กด ■ เพื่อส่ง</span>
                </div>
              )}
            </div>
            <button type="submit" className="bmchat-send" data-testid="chat-send" disabled={busy || !input.trim()} aria-label="ส่ง">
              ➤
            </button>
            {/* ส่งไฟล์เสียงแทนการอัด (ใช้ทดสอบ e2e ด้วย setInputFiles ได้) */}
            <input ref={fileRef} type="file" accept="audio/*" data-testid="voice-file" hidden onChange={onVoiceFile} />
          </form>
        </section>
      )}

      {/* audio element อยู่ตลอด (ไม่ unmount ตอนปิดแผง) ให้เสียงเล่นต่อได้ */}
      <audio
        ref={audioRef}
        data-testid="chat-audio"
        preload="auto"
        onEnded={() => setPlayingKey(null)}
        onPause={() => setPlayingKey(null)}
        style={{ display: 'none' }}
      />
    </div>
  );
}

function MicIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
      <path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
