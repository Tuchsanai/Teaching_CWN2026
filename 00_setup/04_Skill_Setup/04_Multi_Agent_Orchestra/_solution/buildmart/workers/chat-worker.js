// workers/chat-worker.js — แชทบอท "น้องช่าง" (BUILDMART ข้อ 4.4 · CONTRACT หัวข้อ chat-worker)
//
// รับงานจากคิว chat.request (RPC) → ส่ง status 'thinking' ทันที
//   → เตรียม context: ประวัติ 10 ข้อความ + สินค้าที่กำลังคุยถึง (v3) + Hybrid RAG top 20 → rerank → top 4
//     + สินค้าที่เกี่ยวข้องจาก DB + ข้อมูลร้าน/กฎ
//   → เรียก LLM (stream) → ถ้าเจอ tag: [CALC] คำนวณ / [QUOTE] สร้างใบเสนอราคา แล้วเรียกซ้ำ (≤ 2 รอบ) · [ADD_TO_CART] เขียนตะกร้า
//   → stream delta (ข้อความสะสม) ไป exchange chat.reply → done {text, cites, cartCount, quoteNo, retrieved, products}
//   → บันทึก chat_messages (user + assistant) → ack
// error ที่ไม่ใช่ LLM (เช่น DB) → republish พร้อม header x-retries+1 · ครบ 2 ครั้ง → nack(requeue=false) → chat.dlq
// LLM ล่ม/timeout → ตอบขอโทษแบบ type 'done' (ไม่ใช่ error)
import { pool, waitForDb } from './lib/db.js';
import { connectAmqp, replyTo, parseJson, Q } from './lib/amqp.js';
import { markReady, markNotReady } from './lib/ready.js';
import { addToCart, cartCount } from './lib/cart.js';
import { createQuoteFromCart } from './lib/quote.js';
import { chatLLM, llmConfig } from './lib/llm.js';
import { parseTags, cleanText, citeRefs, hasThai } from './lib/tags.js';
import {
  loadHistory, searchDocs, findProducts, buildSystemPrompt, citeThreshold,
  loadProducts, conversationFocus, namesProduct, searchName, buildEstimate, carryCodes, REFER_RE, RERANK_ON,
} from './lib/context.js';
import { aiboxInfo } from './lib/aibox.js';
import { digitsForThaiNumbers } from '../shared/thainum.js';
import { calculate } from '../shared/calc.js';

const PREFETCH = Number(process.env.CHAT_PREFETCH || 4);
const MAX_TOOL_ROUNDS = 2; // เรียก LLM ซ้ำหลังผล tag ได้ไม่เกิน 2 รอบ
const MAX_RETRIES = 2;
const DELTA_EVERY_MS = 50;

const log = (...a) => console.log(new Date().toISOString(), '[chat-worker]', ...a);

// ---------------------------------------------------------------- ข้อความมาตรฐาน
const SORRY = {
  th: 'ขออภัยครับ ตอนนี้ระบบผู้ช่วยตอบกลับไม่ได้ชั่วคราว รบกวนลองใหม่อีกครั้งในอีกสักครู่ หรือโทรสอบถามสาขาลาดกระบัง 02-111-0001 · บางนา 02-111-0002 · รังสิต 02-111-0003 ได้เลยครับ',
  en: 'Sorry, our assistant is temporarily unavailable. Please try again in a moment, or call our branches: Lat Krabang 02-111-0001 · Bang Na 02-111-0002 · Rangsit 02-111-0003.',
};
const FAILED = {
  th: 'ขออภัยครับ ระบบขัดข้อง ไม่สามารถตอบคำถามนี้ได้ รบกวนลองใหม่อีกครั้งครับ',
  en: 'Sorry, something went wrong and I could not answer this. Please try again.',
};

// ---------------------------------------------------------------- tag → ทำงานจริง
function runCalc(args) {
  const { type, ...input } = args || {};
  try {
    const res = calculate(type, input);
    return { type, input, ...res };
  } catch (e) {
    return { type: type ?? null, error: e.message };
  }
}

async function runQuote(sessionId) {
  try {
    const q = await createQuoteFromCart(pool, sessionId, {});
    return { quoteNo: q.quoteNo, total: q.totals.total };
  } catch (e) {
    if (e.message === 'cart_empty') return { error: 'empty cart' };
    throw e;
  }
}

// ---------------------------------------------------------------- อ้างอิงเอกสาร (cites)
// ชิ้นตัวอักษรยาว 5 (ไม่สนช่องว่าง) — ใช้ตรวจว่าคำตอบ "ใช้ข้อความจาก chunk จริง" ไหม
const norm = (s) => String(s || '').toLowerCase().replace(/[\s*_`"'“”()\[\]{}:·•,.!?|-]+/g, '');
function shingles(s, n = 5) {
  const a = Array.from(norm(s));
  const out = new Set();
  for (let i = 0; i + n <= a.length; i++) out.add(a.slice(i, i + n).join(''));
  return out;
}
/** จำนวนชิ้นของคำตอบที่พบใน chunk แต่ไม่มีใน context ส่วนอื่น (ข้อมูลร้าน/ตารางสินค้า/คำถาม/ประวัติ) */
function groundedHits(answerText, chunk, excludeSet) {
  const c = norm(chunk);
  let hits = 0;
  for (const g of shingles(answerText)) if (!excludeSet.has(g) && c.includes(g)) hits++;
  return hits;
}
const GROUND_MIN_HITS = 8; // วัดจริง: คำถามทั่วไป 0–4 · คำตอบจากเอกสาร 12–86

/**
 * cites ที่ส่งให้ web: chunk ที่โมเดลอ้าง [n]
 * ไม่มี [n] → chunk อันดับ 1–2 ที่ vecSim ≥ เกณฑ์ **และ** คำตอบมีข้อความจาก chunk นั้นจริง (กันคำถามทั่วไปได้ cite มั่ว
 * เพราะ e5-small ให้ vecSim สูงกับทุกเอกสารในหมวดเดียวกัน เช่น "ปูนซีเมนต์ถุงละเท่าไร" ≈ 0.90 กับ BM-DS-CEM)
 */
async function makeCites(raw, docs, { allowFallback, answerText = '', excludeText = '' }) {
  const pick = (d) => ({ filename: d.filename, page: d.page, snippet: d.content.replace(/\s+/g, ' ').trim().slice(0, 180) });
  const seen = new Set();
  const out = [];
  const push = (d) => {
    const k = `${d.filename}#${d.page}`;
    if (!seen.has(k)) {
      seen.add(k);
      out.push(pick(d));
    }
  };
  for (const n of citeRefs(raw)) if (docs[n - 1]) push(docs[n - 1]);
  if (!out.length && allowFallback) {
    const thr = await citeThreshold();
    const ex = shingles(excludeText);
    for (const d of docs.slice(0, 2)) if (d.vecSim != null && d.vecSim >= thr && groundedHits(answerText, d.content, ex) >= GROUND_MIN_HITS) push(d);
  }
  return out;
}

// ---------------------------------------------------------------- งานหลักของ 1 ข้อความ
async function answer(body, emit) {
  const sessionId = String(body.sessionId || 'anonymous');
  const question = String(body.text || '').trim().slice(0, 2000);
  // ตัวเลขที่สะกดเป็นคำ (ข้อความจาก Whisper เช่น "ร้อยถุง") → ตัวเลข ให้ LLM/การค้นเห็นจำนวนชัด ๆ (บันทึกประวัติด้วยข้อความเดิม)
  const askQ = digitsForThaiNumbers(question).replace(/\s{2,}/g, ' ').trim();
  const en = body.lang ? body.lang === 'en' : !hasThai(question);
  const lang = en ? 'en' : 'th';

  if (question === '__bm_test_fail__') throw new Error('test failure (DLQ hook)');

  // ประวัติ: ข้อความลูกค้าแปลงตัวเลขคำไทยเป็นตัวเลขด้วย ("หกสิบคูณหกสิบ" → 60x60) ให้ LLM/การค้นอ่านง่าย
  const history = (await loadHistory(pool, sessionId)).map((m) => (m.role === 'user' ? { ...m, content: digitsForThaiNumbers(m.content).replace(/\s{2,}/g, ' ').trim() } : m));
  const rows = await loadProducts(pool);
  // v3: สินค้าที่กำลังคุยถึง — คำถามต่อเนื่อง ("อันนั้นเก็บได้นานแค่ไหน") เติมชื่อสินค้าเข้าไปในคำค้นเอกสาร
  const focus = conversationFocus(rows, history, askQ);
  const followUp = focus.products.length > 0 && (REFER_RE.test(askQ) || !namesProduct(askQ, rows));
  // คำถามต่อเนื่อง ("แล้วต้องใช้ปูนกาวกี่กิโลต่อตารางเมตร") พารหัส/ขนาดจากคำถามก่อนหน้า (60x60 · DB12) ไปค้นด้วย
  const baseQuery = carryCodes(askQ, history);
  const searchQuery = followUp ? `${baseQuery} ${focus.products.map(searchName).join(' ')}` : baseQuery;
  const estimate = await buildEstimate(pool, sessionId, focus, { question: askQ, rows }).catch(() => null);
  const docs = await searchDocs(pool, searchQuery, 4);
  const products = await findProducts(pool, askQ, history, docs, 8, { rows, focus });
  const messages = [
    { role: 'system', content: buildSystemPrompt({ products, docs, en, focus, estimate }) },
    ...history,
    { role: 'user', content: askQ },
  ];

  // v3: token จริงจาก LLM (usage) รวมทุกรอบ tag → done.usage (load test ใช้คิด tokens/s)
  const usage = { completion_tokens: 0, prompt_tokens: 0, decode_ms: 0, rounds: 0, source: null };
  let quoteNo = null;
  let cartChanged = false;
  let toolUsed = false;
  let finalRaw = '';
  let llmFailed = false;

  for (let round = 0; round <= MAX_TOOL_ROUNDS; round++) {
    let toolRound = false;
    let raw;
    try {
      raw = await chatLLM(messages, {
        onUsage: (u) => {
          if (u.completion_tokens != null) {
            usage.completion_tokens += Number(u.completion_tokens) || 0;
            usage.prompt_tokens += Number(u.prompt_tokens) || 0;
            usage.rounds++;
            usage.source = 'llm_usage';
          }
          if (u.timings?.predicted_ms) usage.decode_ms += Number(u.timings.predicted_ms) || 0;
        },
        onDelta: (soFar) => {
          if (toolRound) return;
          if (round < MAX_TOOL_ROUNDS && parseTags(soFar).some((t) => t.name !== 'ADD_TO_CART')) {
            toolRound = true; // รอบนี้มี tag ที่ต้องเรียกซ้ำ → ไม่ stream ต่อ
            return;
          }
          const text = cleanText(soFar);
          if (text) emit.delta(text);
        },
      });
    } catch (e) {
      console.warn('[chat-worker] LLM failed:', e.message);
      llmFailed = true;
      break;
    }
    finalRaw = raw;
    const tags = parseTags(raw);

    for (const t of tags.filter((x) => x.name === 'ADD_TO_CART')) {
      const items = Array.isArray(t.args) ? t.args : Array.isArray(t.args?.items) ? t.args.items : [t.args];
      for (const it of items) {
        if (!it?.sku) continue;
        try {
          await addToCart(pool, sessionId, it.sku, it.qty);
          cartChanged = true;
          toolUsed = true;
        } catch (e) {
          console.warn('[chat-worker] add to cart failed:', it.sku, e.message);
        }
      }
    }

    if (round >= MAX_TOOL_ROUNDS) break;
    const calc = tags.find((x) => x.name === 'CALC');
    const quote = tags.find((x) => x.name === 'QUOTE');
    if (!calc && !quote) break;

    toolUsed = true;
    messages.push({ role: 'assistant', content: stripThinkKeepTags(raw) });
    if (calc) {
      messages.push({ role: 'user', content: 'ผลคำนวณ: ' + JSON.stringify(runCalc(calc.args)) });
    } else {
      const res = await runQuote(sessionId);
      if (res.quoteNo) quoteNo = res.quoteNo;
      messages.push({ role: 'user', content: 'ผลคำสั่ง: ' + JSON.stringify(res) });
    }
  }

  let text;
  let cites = [];
  if (llmFailed) {
    text = SORRY[lang];
    if (quoteNo) text += en ? `\nYour quotation number: ${quoteNo} (/quote/${quoteNo})` : `\nเลขที่ใบเสนอราคา ${quoteNo} (ดูได้ที่ /quote/${quoteNo}) ครับ`;
  } else {
    text = cleanText(finalRaw, { final: true });
    if (quoteNo && !text.includes(quoteNo)) text += en ? `\nQuotation number: ${quoteNo} (/quote/${quoteNo})` : `\nเลขที่ใบเสนอราคา ${quoteNo} ดูได้ที่ /quote/${quoteNo} ครับ`;
    if (!text) text = en ? 'Sorry, I could not find an answer. Could you rephrase your question?' : 'ขออภัยครับ ผมยังหาคำตอบไม่ได้ รบกวนถามใหม่อีกครั้งได้ไหมครับ';
    const excludeText = [buildSystemPrompt({ products, docs: [], en }), question, ...history.map((m) => m.content)].join('\n');
    cites = await makeCites(finalRaw, docs, { allowFallback: !toolUsed, answerText: text, excludeText });
  }
  if (process.env.CHAT_DEBUG) log('raw', JSON.stringify(finalRaw).slice(0, 400), 'docs', docs.map((d) => `${d.filename}#${d.page}:${d.vecSim}`).join(' '));
  const count = await cartCount(pool, sessionId);
  const retrieved = docs.map((d) => ({ filename: d.filename, page: d.page, score: d.rerankScore ?? d.score, hybridRank: d.hybridRank }));
  if (usage.decode_ms) usage.decode_tok_s = +(usage.completion_tokens / (usage.decode_ms / 1000)).toFixed(1);
  usage.decode_ms = Math.round(usage.decode_ms);
  return { sessionId, question, text, cites, cartCount: count, cartChanged, quoteNo, llmFailed, usage: usage.source ? usage : undefined, retrieved, products: products.map((p) => p.sku), focus: focus.skus };
}

/** ข้อความ assistant ที่ส่งกลับให้ LLM ในรอบ tag: ตัด think แต่คง tag ไว้ (ตาม Notes from C3) */
function stripThinkKeepTags(raw) {
  return String(raw).replace(/<think>[\s\S]*?<\/think>/g, '').replace(/^[\s\S]*<\/think>/, '').trim();
}

async function saveChat(r) {
  const c = await pool.connect();
  try {
    await c.query('BEGIN');
    await c.query('INSERT INTO chat_sessions (id) VALUES ($1) ON CONFLICT (id) DO NOTHING', [r.sessionId]);
    await c.query(`INSERT INTO chat_messages (session_id, role, content) VALUES ($1, 'user', $2)`, [r.sessionId, r.question]);
    await c.query(`INSERT INTO chat_messages (session_id, role, content, cites) VALUES ($1, 'assistant', $2, $3)`, [
      r.sessionId,
      r.text,
      JSON.stringify(r.cites || []),
    ]);
    await c.query('COMMIT');
  } catch (e) {
    await c.query('ROLLBACK').catch(() => {});
    throw e;
  } finally {
    c.release();
  }
}

// ---------------------------------------------------------------- RabbitMQ
function makeEmitter(ch, msg, messageId) {
  let last = '';
  let pending = null;
  let timer = null;
  let lastAt = 0;
  let closed = false;
  const flush = () => {
    timer = null;
    if (closed || pending == null || pending === last) return;
    last = pending;
    lastAt = Date.now();
    replyTo(ch, msg, { messageId, type: 'delta', text: pending });
  };
  return {
    status: (status) => replyTo(ch, msg, { messageId, type: 'status', status }),
    delta(text) {
      pending = text;
      if (!timer) timer = setTimeout(flush, Math.max(0, DELTA_EVERY_MS - (Date.now() - lastAt)));
    },
    close() {
      closed = true;
      if (timer) clearTimeout(timer);
      timer = null;
    },
  };
}

let inFlight = 0;

async function onMessage(ch, msg) {
  if (!msg) return; // consumer ถูกยกเลิก
  const body = parseJson(msg);
  if (!body || typeof body !== 'object') {
    console.warn('[chat-worker] bad message → DLQ');
    ch.nack(msg, false, false);
    return;
  }
  const messageId = body.messageId || msg.properties.correlationId || null;
  const retries = Number(msg.properties.headers?.['x-retries'] || 0);
  const t0 = Date.now();
  inFlight++;
  const emit = makeEmitter(ch, msg, messageId);
  try {
    emit.status('thinking');
    const r = await answer(body, emit);
    emit.close();
    await saveChat(r);
    replyTo(ch, msg, {
      messageId,
      type: 'done',
      text: r.text,
      cites: r.cites,
      cartCount: r.cartCount,
      quoteNo: r.quoteNo || undefined,
      retrieved: r.retrieved,
      products: r.products,
      usage: r.usage,
    });
    ch.ack(msg);
    log(`done ${messageId} ${Date.now() - t0}ms cites=${r.cites.length} cart=${r.cartCount}${r.focus?.length ? ' focus=' + r.focus.join(',') : ''}${r.quoteNo ? ' ' + r.quoteNo : ''}${r.llmFailed ? ' (LLM down)' : ''}`);
  } catch (e) {
    emit.close();
    console.error(`[chat-worker] error ${messageId} (retry ${retries}):`, e.message);
    try {
      if (retries >= MAX_RETRIES) {
        const lang = body.lang === 'en' || (!body.lang && !hasThai(body.text)) ? 'en' : 'th';
        replyTo(ch, msg, { messageId, type: 'error', text: FAILED[lang] });
        ch.nack(msg, false, false); // → chat.dlq (dead-letter)
      } else {
        const { headers = {}, ...props } = msg.properties;
        ch.sendToQueue(Q.CHAT_REQUEST, msg.content, {
          ...Object.fromEntries(Object.entries(props).filter(([, v]) => v !== undefined)),
          persistent: true,
          headers: { ...headers, 'x-retries': retries + 1 },
        });
        ch.ack(msg);
      }
    } catch (e2) {
      console.error('[chat-worker] retry/DLQ failed:', e2.message);
    }
  } finally {
    inFlight--;
  }
}

async function startConsuming({ ch }) {
  await ch.prefetch(PREFETCH);
  await ch.consume(Q.CHAT_REQUEST, (msg) => onMessage(ch, msg).catch((e) => console.error('[chat-worker] handler crash', e)), { noAck: false });
  markReady(`chat-worker mode=${llmConfig.mode}`);
  const ab = aiboxInfo('rerank');
  log(`consuming ${Q.CHAT_REQUEST} prefetch=${PREFETCH} mode=${llmConfig.mode} llm=${llmConfig.baseUrl}${llmConfig.model ? ' model=' + llmConfig.model : ''} rerank=${RERANK_ON ? 'on' : 'off'} aibox=${ab.url}${ab.mock ? ' (mock)' : ''}`);
}

// ---------------------------------------------------------------- main
await waitForDb();
const amqp = await connectAmqp({
  prefetch: PREFETCH,
  onReconnect: async (again) => {
    current = again;
    await startConsuming(again);
  },
});
let current = amqp;
await startConsuming(amqp);

const stop = async (sig) => {
  log(`${sig} → shutting down (in flight ${inFlight}, unacked messages go back to the queue)`);
  markNotReady();
  try {
    await current.ch.close();
  } catch {}
  try {
    await current.conn.close();
  } catch {}
  await pool.end().catch(() => {});
  process.exit(0);
};
process.on('SIGTERM', () => stop('SIGTERM'));
process.on('SIGINT', () => stop('SIGINT'));
