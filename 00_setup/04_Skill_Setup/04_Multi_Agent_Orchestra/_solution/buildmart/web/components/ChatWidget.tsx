'use client';
// components/ChatWidget.tsx — แชทบอท "น้องช่าง" ลอยมุมขวาล่างทุกหน้า (C1)
// - ส่งคำถาม POST /api/chat → อ่าน SSE: queued → status → delta (ข้อความสะสม) → done | error
// - ประวัติ: GET /api/chat/history ตอนเปิดครั้งแรก
// - อ่านออกเสียง: GET /api/tts/status → ปุ่ม 🔊 (tts-play) + สวิตช์ tts-auto · POST /api/tts → <audio data-testid="chat-audio">
// - บอทใส่ตะกร้า → done.cartCount → window event 'bm:cart' ให้ Header อัปเดตตัวเลข
// - e2e: window.__bmAudio = {audioId, startedAt, durationMs} และ window.__bmAudioLog (array)
import { Fragment, useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import './ChatWidget.css';

type Cite = { filename: string; page: number; snippet?: string };
type Phase = 'queued' | 'thinking' | 'streaming' | 'done' | 'error';
type Msg = {
  key: string;
  role: 'user' | 'bot';
  text: string;
  phase: Phase;
  cites?: Cite[];
  quoteNo?: string;
  audioId?: string;
  durationMs?: number;
  ttsLoading?: boolean;
  ttsError?: boolean;
};

const SUGGESTIONS = ['ร้านเปิดกี่โมง', 'เทคอนกรีต 3 คิวใช้ปูนกี่ถุง', 'ปูนเก็บได้นานแค่ไหน'];
const AUTO_KEY = 'bm_tts_auto';

declare global {
  interface Window {
    __bmAudio?: { audioId: string; startedAt: number; durationMs: number | null };
    __bmAudioLog?: { audioId: string; startedAt: number; durationMs: number | null }[];
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

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [ttsOn, setTtsOn] = useState(false);
  const [auto, setAuto] = useState(false);
  const [playingKey, setPlayingKey] = useState<string | null>(null);
  const historyLoaded = useRef(false);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const msgsRef = useRef<Msg[]>([]);
  const autoRef = useRef(false);
  const ttsRef = useRef(false);
  msgsRef.current = msgs;
  autoRef.current = auto;
  ttsRef.current = ttsOn;

  const patch = useCallback((key: string, p: Partial<Msg>) => {
    setMsgs((cur) => cur.map((m) => (m.key === key ? { ...m, ...p } : m)));
  }, []);

  // ---------- เริ่มต้น ----------
  useEffect(() => {
    if (!window.__bmAudioLog) window.__bmAudioLog = [];
    try {
      setAuto(localStorage.getItem(AUTO_KEY) === '1');
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

  useEffect(() => {
    refreshTts();
  }, [refreshTts]);

  useEffect(() => {
    if (!open) return;
    refreshTts();
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
  }, [open, refreshTts]);

  // เลื่อนลงล่างสุดเมื่อมีข้อความใหม่
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [msgs, open]);

  // ---------- เสียง ----------
  const playAudio = useCallback(async (key: string, audioId: string, durationMs: number | null) => {
    const a = audioRef.current;
    if (!a) return;
    a.pause();
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
  }, []);

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
    async (raw: string) => {
      const text = raw.trim();
      if (!text || busy) return;
      setBusy(true);
      setInput('');
      const botKey = newKey();
      setMsgs((cur) => [
        ...cur,
        { key: newKey(), role: 'user', text, phase: 'done' },
        { key: botKey, role: 'bot', text: '', phase: 'queued' },
      ]);
      let finished = false;
      const fail = (msg: string) => {
        finished = true;
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
              patch(botKey, { phase: 'streaming', text: clean(String(data?.text ?? '')) });
              break;
            case 'done': {
              finished = true;
              const finalText = clean(String(data?.text ?? '')) || 'ขออภัยครับ ไม่ได้รับคำตอบ';
              patch(botKey, {
                phase: 'done',
                text: finalText,
                cites: uniqCites(data?.cites),
                quoteNo: data?.quoteNo || undefined,
              });
              if (typeof data?.cartCount === 'number') {
                window.dispatchEvent(new CustomEvent('bm:cart', { detail: { count: data.cartCount } }));
              }
              if (autoRef.current && ttsRef.current) {
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
        setBusy(false);
        setTimeout(() => inputRef.current?.focus(), 0);
      }
    },
    [busy, patch, speak],
  );

  const toggleAuto = (v: boolean) => {
    setAuto(v);
    try {
      localStorage.setItem(AUTO_KEY, v ? '1' : '0');
    } catch {
      /* ignore */
    }
  };

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
            💬
          </span>
          <span className="bmchat-fab-label">ถามน้องช่าง</span>
        </button>
      )}

      {open && (
        <section className="bmchat-panel" data-testid="chat-panel" role="dialog" aria-label="แชทกับน้องช่าง">
          <header className="bmchat-head">
            <div className="bmchat-avatar" aria-hidden>
              🤖
            </div>
            <div className="bmchat-title">
              <b>น้องช่าง 🤖 BuildMart</b>
              <span>{busy ? 'กำลังตอบ…' : 'ผู้ช่วยเรื่องวัสดุก่อสร้าง · ตอบทันที 24 ชม.'}</span>
            </div>
            {ttsOn && (
              <label className="bmchat-switch" title="อ่านออกเสียงคำตอบอัตโนมัติ">
                <input
                  type="checkbox"
                  data-testid="tts-auto"
                  checked={auto}
                  onChange={(e) => toggleAuto(e.target.checked)}
                />
                <span className="bmchat-switch-track" aria-hidden>
                  <span className="bmchat-switch-knob" />
                </span>
                <span className="bmchat-switch-text">อ่านออกเสียงอัตโนมัติ</span>
              </label>
            )}
            <button type="button" className="bmchat-close" aria-label="ปิดแชท" data-testid="chat-close" onClick={() => setOpen(false)}>
              ✕
            </button>
          </header>

          <div className="bmchat-list" ref={listRef} aria-live="polite">
            <div className="bmchat-welcome">
              สวัสดีครับ ผม <b>น้องช่าง</b> 👷 ถามได้ทั้งราคา สต็อก 3 สาขา คำนวณวัสดุ ใส่ตะกร้า หรือขอใบเสนอราคาครับ
            </div>
            {msgs.map((m) =>
              m.role === 'user' ? (
                <div key={m.key} className="bmchat-row user">
                  <div className="bmchat-bubble user" data-testid="chat-msg-user">
                    {m.text}
                  </div>
                </div>
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
                      className={`bmchat-bubble bot${m.phase === 'error' ? ' error' : ''}`}
                      data-testid="chat-msg-bot"
                      data-done={m.phase === 'done' || m.phase === 'error' ? 'true' : 'false'}
                    >
                      <Markdown text={m.text} />
                      {m.phase === 'streaming' && <span className="bmchat-caret" aria-hidden />}
                    </div>
                  )}
                  {m.phase === 'done' && (m.cites?.length || m.quoteNo || ttsOn) ? (
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
                          {m.ttsLoading ? <span className="bmchat-spin" aria-hidden /> : <span aria-hidden>🔊</span>}
                          {m.ttsLoading ? 'กำลังสร้างเสียง…' : m.ttsError ? 'ลองอีกครั้ง' : 'ฟัง'}
                        </button>
                      )}
                    </div>
                  ) : null}
                </div>
              ),
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
            className="bmchat-form"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <textarea
              ref={inputRef}
              className="bmchat-input"
              data-testid="chat-input"
              rows={1}
              placeholder="พิมพ์คำถาม เช่น ปูนซีเมนต์ถุงละเท่าไร"
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
            <button type="submit" className="bmchat-send" data-testid="chat-send" disabled={busy || !input.trim()} aria-label="ส่ง">
              ➤
            </button>
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
