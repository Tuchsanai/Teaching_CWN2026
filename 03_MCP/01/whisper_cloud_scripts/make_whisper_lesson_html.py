"""make_whisper_lesson_html.py — ประกอบ whisper_lesson_data.json เป็น whisper_lesson.html ไฟล์เดียว"""
import json, pathlib, sys
src = pathlib.Path(__file__).with_name("whisper_lesson_data.json")
dst = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("whisper_lesson.html")
data = json.loads(src.read_text())
fb = src.with_name("yt_fallback.mp3")           # เสียงต้นฉบับบีบอัด (mono 32 kbps) สำหรับโหมดไม่มี YouTube
if fb.exists():
    import base64
    data["fallback_audio"] = "data:audio/mpeg;base64," + base64.b64encode(fb.read_bytes()).decode()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

HTML = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>Whisper Lesson · __TITLE__</title>
<style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1f2328;--muted:#6b7280;--line:#e5e1d8;--accent:#b4531b;--accent-soft:#fbe7d8;--zh:#155e75;--zh-soft:#d9f0f7;--hl:#ffe36e;--done:#9ca3af}
@media (prefers-color-scheme:dark){:root{--bg:#16181d;--card:#1f232b;--ink:#e8e6e1;--muted:#9aa0aa;--line:#2f343d;--accent:#f0925a;--accent-soft:#3a2a1f;--zh:#7dd3fc;--zh-soft:#16303b;--hl:#d4b000;--done:#6b7280}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans Thai","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif}
header{padding:28px 24px 12px;max-width:1100px;margin:0 auto}
h1{font-size:22px;margin:0 0 6px}
.meta{color:var(--muted);font-size:13px;display:flex;gap:14px;flex-wrap:wrap}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:600}
main{max-width:1100px;margin:0 auto;padding:0 24px 60px;display:grid;gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.card h2{font-size:15px;margin:0 0 10px;color:var(--muted);font-weight:600;letter-spacing:.02em;text-transform:uppercase}
.video{position:relative;width:100%;aspect-ratio:16/9;border-radius:10px;overflow:hidden;background:#000}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
/* timeline */
.tl{position:relative;height:56px;display:flex;gap:1px;border-radius:8px;overflow:hidden;background:var(--line);cursor:pointer}
.tl .seg{flex:0 0 auto;height:100%;background:#cfd8dc;opacity:.85;transition:opacity .15s}
.tl .seg.zh{background:var(--zh);opacity:.55}
.tl .seg:hover{opacity:1}
.tl .seg.active{outline:2px solid var(--accent);outline-offset:-2px;opacity:1;background:var(--accent)}
.tl .cursor{position:absolute;top:0;bottom:0;width:2px;background:var(--ink);pointer-events:none}
.tl-labels{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-top:6px}
.legend{display:flex;gap:16px;font-size:12px;color:var(--muted);margin-top:6px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:4px}
/* transcript */
.tbl{max-height:420px;overflow:auto;border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{position:sticky;top:0;background:var(--card);text-align:left;color:var(--muted);font-weight:600;padding:8px 10px;border-bottom:1px solid var(--line);font-size:12px}
td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
td.t{white-space:nowrap;color:var(--muted);font-variant-numeric:tabular-nums;cursor:pointer;width:64px}
td.t:hover{color:var(--accent)}
tr.active td{background:var(--accent-soft)}
tr.first3 td.t{border-left:3px solid var(--zh)}
td.zh{color:var(--zh)}
.play{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:4px 10px;cursor:pointer;font:inherit;font-size:13px}
.play:hover{border-color:var(--accent);color:var(--accent)}
.play.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.play.on{background:var(--zh);color:#fff;border-color:var(--zh)}
/* reading panel */
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.sent{padding:12px 12px 10px;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;background:var(--card)}
.sent.playing{border-color:var(--zh);box-shadow:0 0 0 3px var(--zh-soft)}
.sent .src{color:var(--muted);font-size:13px;margin-bottom:6px}
.sent .row{display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap}
.words{display:flex;flex-wrap:wrap;gap:2px 6px;flex:1;min-width:260px}
.w{display:inline-flex;flex-direction:column;align-items:center;padding:2px 4px;border-radius:6px;cursor:pointer;line-height:1.2;transition:background .1s}
.w .han{font-size:24px}
.w .py{font-size:11px;color:var(--muted);margin-top:2px}
.w.punct{cursor:default}.w.punct .han{color:var(--muted)}
.w:hover{background:var(--zh-soft)}
.w.hl{background:var(--hl);color:#1f2328}.w.hl .py{color:#1f2328}
.w.done .han{color:var(--done)}
.btns{display:flex;gap:6px;align-items:center;white-space:nowrap}
.time{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.notice{display:none;margin-top:10px;padding:10px 12px;border-radius:10px;background:var(--accent-soft);color:var(--ink);font-size:13px;line-height:1.5}
.notice.show{display:block}
.notice a{color:var(--accent);font-weight:600}
.abar{display:none;gap:10px;align-items:center;margin-top:10px;flex-wrap:wrap}
.abar.show{display:flex}
.abar .tm{font-variant-numeric:tabular-nums;color:var(--muted);font-size:13px}
.abar input[type=range]{flex:1;min-width:200px;accent-color:var(--accent)}
footer{max-width:1100px;margin:0 auto;padding:0 24px 40px;color:var(--muted);font-size:12px;line-height:1.7}
kbd{font:inherit;font-size:12px;padding:0 5px;border:1px solid var(--line);border-radius:4px}
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="meta">
    <span>ต้นฉบับ: <b id="lang"></b></span><span>ความยาว <b id="dur"></b></span><span id="segcount"></span>
    <span class="badge">whisper-cloud · RTX 4090 · Streamable HTTP</span>
  </div>
</header>
<main>
  <section class="card">
    <div class="video"><div id="player"></div></div>
    <div class="notice" id="notice"></div>
    <div class="abar" id="abar">
      <button class="play primary" id="aPlay">▶ เล่นเสียงต้นฉบับ</button>
      <span class="tm" id="aTime">0:00</span><input type="range" id="aSeek" min="0" max="100" value="0" step="0.1"><span class="tm" id="aDur"></span>
      <a class="play" id="ytLink" target="_blank" rel="noopener">เปิดบน YouTube ↗</a>
    </div>
  </section>

  <section class="card">
    <h2>Timeline ทั้งคลิป <span style="float:right;text-transform:none;font-weight:400" id="now">0:00</span></h2>
    <div class="tl" id="tl"><div class="cursor" id="cursor" style="left:0"></div></div>
    <div class="tl-labels"><span>0:00</span><span id="mid"></span><span id="end"></span></div>
    <div class="legend"><span><i style="background:var(--zh);opacity:.55"></i>3 นาทีแรก แปลจีน + เสียง Kokoro</span><span><i style="background:#cfd8dc"></i>ถอดเสียงอย่างเดียว</span><span><i style="background:var(--accent)"></i>กำลังเล่น</span></div>
  </section>

  <section class="card">
    <h2>ถอดเสียง (Whisper large-v3)</h2>
    <div class="tbl" id="tblwrap"><table><thead><tr><th>เวลา</th><th>ต้นฉบับ</th><th>คำแปลจีน (0:00–3:00)</th></tr></thead><tbody id="rows"></tbody></table></div>
  </section>

  <section class="card">
    <h2>ฝึกอ่านภาษาจีน 3 นาทีแรก (Kokoro)</h2>
    <div class="controls">
      <button class="play primary" id="playAll">▶ เล่นต่อเนื่องทั้ง 3 นาที</button>
      <button class="play" id="playAllSlow">🐢 เล่นช้า 0.7x</button>
      <button class="play" id="stopAll">■ หยุด</button>
      <span class="time">คลิกคำเดี่ยว ๆ เพื่อฟังเฉพาะคำนั้น · ตอนเล่นเสียงจีน วิดีโอจะหยุดชั่วคราว</span>
    </div>
    <div id="sents"></div>
  </section>
</main>
<footer>
  สร้างจาก prompt เดียวใน Claude Code: skill vastai เช่า RTX 4090 → MCP server <code>whisper-cloud</code> (Streamable HTTP ผ่าน SSH tunnel) → tools
  <code>transcribe_youtube</code> · <code>translate_segments</code> (NLLB-200) · <code>speak_zh</code> (Kokoro-82M สังเคราะห์ทีละคำ) → ไฟล์นี้ · โหลดจากเน็ตเฉพาะ YouTube IFrame API เท่านั้น เสียงจีนและเสียงต้นฉบับ (mono 32 kbps) ฝัง base64 ในไฟล์ จึงเปิดออฟไลน์ได้
</footer>

<script type="application/json" id="data">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const fmt = s => { s = Math.max(0, Math.floor(s)); return Math.floor(s/60) + ':' + String(s%60).padStart(2,'0'); };
document.getElementById('lang').textContent = ({th:'ไทย',en:'อังกฤษ',zh:'จีน',ja:'ญี่ปุ่น'})[D.language] || D.language;
document.getElementById('dur').textContent = fmt(D.duration);
document.getElementById('segcount').textContent = D.segments.length + ' segments · แปลจีน ' + D.first3.length + ' ประโยค';
document.getElementById('mid').textContent = fmt(D.duration/2);
document.getElementById('end').textContent = fmt(D.duration);
const zhBy = {}; D.first3.forEach(s => zhBy[s.start] = s);

/* ---------- แหล่งเวลา: YouTube (ถ้าเล่นได้) หรือเสียงต้นฉบับที่ฝังในไฟล์ ---------- */
let player, ready = false, mode = 'video';          // 'video' | 'audio'
const notice = document.getElementById('notice'), abar = document.getElementById('abar');
const fbAudio = D.fallback_audio ? new Audio(D.fallback_audio) : null;
document.getElementById('ytLink').href = D.url;
const YT_ERR = { 2: 'พารามิเตอร์วิดีโอไม่ถูกต้อง', 5: 'เบราว์เซอร์เล่น HTML5 player ไม่ได้', 100: 'ไม่พบวิดีโอหรือเป็นวิดีโอส่วนตัว', 101: 'เจ้าของวิดีโอไม่อนุญาตให้ฝัง', 150: 'เจ้าของวิดีโอไม่อนุญาตให้ฝัง', 153: 'YouTube ปฏิเสธ embed ที่ไม่มี referrer (เปิดไฟล์แบบ file:// หรือไม่ส่ง referrer)' };
function useAudioMode(why) {
  if (mode === 'audio') return;
  mode = 'audio';
  notice.innerHTML = why + (fbAudio ? ' — สลับเป็น <b>เสียงต้นฉบับที่ฝังในไฟล์</b> แทน Timeline และตารางยังทำงานตามเดิม' : ' — ไม่มีเสียงต้นฉบับฝังอยู่ ใช้ได้เฉพาะเสียงจีนของ Kokoro') + ' · หากต้องการภาพวิดีโอ ให้เปิดไฟล์ผ่าน http เช่น <code>python -m http.server</code> หรือกด "เปิดบน YouTube"';
  notice.classList.add('show'); if (fbAudio) abar.classList.add('show');
}
if (location.protocol === 'file:') useAudioMode('เปิดไฟล์แบบ file:// ซึ่ง YouTube ไม่อนุญาตให้ฝังวิดีโอ (error 153)');
const tag = document.createElement('script'); tag.src = 'https://www.youtube.com/iframe_api';
tag.onerror = () => useAudioMode('โหลด YouTube IFrame API ไม่ได้ (ไม่มีอินเทอร์เน็ต?)'); document.head.appendChild(tag);
const ytTimeout = setTimeout(() => { if (!ready) useAudioMode('ตัวเล่น YouTube ไม่พร้อมภายใน 10 วินาที (ไม่มีอินเทอร์เน็ต หรือถูกบล็อก)'); }, 10000);
window.onYouTubeIframeAPIReady = () => {
  player = new YT.Player('player', { videoId: D.video_id, playerVars: { rel: 0, playsinline: 1 },
    events: { onReady: () => { ready = true; clearTimeout(ytTimeout); if (mode === 'video') { notice.classList.remove('show'); } },
              onError: e => useAudioMode('YouTube ตอบ error ' + e.data + ': ' + (YT_ERR[e.data] || 'เล่นไม่ได้')) } });
};
const nowTime = () => mode === 'audio' ? (fbAudio ? fbAudio.currentTime : 0) : (ready && player.getCurrentTime ? player.getCurrentTime() : 0);
const seek = t => {
  if (mode === 'audio') { if (fbAudio) { stopAll(); fbAudio.currentTime = t; fbAudio.play(); } return; }
  if (ready) { player.seekTo(t, true); player.playVideo(); }
};
const pauseVideo = () => { if (fbAudio && !fbAudio.paused) fbAudio.pause(); if (ready && player.getPlayerState && player.getPlayerState() === 1) player.pauseVideo(); };
/* แถบควบคุมเสียงต้นฉบับ */
if (fbAudio) {
  const aPlay = document.getElementById('aPlay'), aSeek = document.getElementById('aSeek'), aTime = document.getElementById('aTime'), aDur = document.getElementById('aDur');
  aSeek.max = D.duration; aDur.textContent = fmt(D.duration);
  aPlay.onclick = () => { if (fbAudio.paused) { stopAll(); fbAudio.play(); } else fbAudio.pause(); };
  fbAudio.onplay = () => aPlay.textContent = '❚❚ หยุดชั่วคราว'; fbAudio.onpause = () => aPlay.textContent = '▶ เล่นเสียงต้นฉบับ';
  aSeek.oninput = () => { fbAudio.currentTime = +aSeek.value; };
  setInterval(() => { if (!fbAudio.paused || document.activeElement !== aSeek) { aSeek.value = fbAudio.currentTime; aTime.textContent = fmt(fbAudio.currentTime); } }, 250);
}

/* ---------- Timeline ---------- */
const tl = document.getElementById('tl'), cursor = document.getElementById('cursor');
const tlSegs = D.segments.map(s => {
  const el = document.createElement('div'); el.className = 'seg' + (zhBy[s.start] ? ' zh' : '');
  el.style.width = Math.max(0.15, (s.end - s.start) / D.duration * 100) + '%';
  el.title = fmt(s.start) + ' ' + s.text; el.onclick = () => seek(s.start); tl.appendChild(el); return el;
});

/* ---------- Transcript table ---------- */
const rows = document.getElementById('rows'), wrap = document.getElementById('tblwrap');
const trs = D.segments.map((s, i) => {
  const z = zhBy[s.start]; const tr = document.createElement('tr'); if (z) tr.className = 'first3';
  tr.innerHTML = `<td class="t" title="ไปที่เวลานี้">${fmt(s.start)}</td><td>${esc(s.text)}</td><td class="zh">${z ? esc(z.zh) + ` <button class="play" data-i="${D.first3.indexOf(z)}" style="margin-left:6px">▶</button>` : ''}</td>`;
  tr.querySelector('.t').onclick = () => seek(s.start);
  const b = tr.querySelector('button'); if (b) b.onclick = () => playSentence(+b.dataset.i, 1);
  rows.appendChild(tr); return tr;
});
function esc(t){ return String(t).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

let lastActive = -1;
function tick() {
  if (mode === 'audio' ? !!fbAudio : (ready && player.getCurrentTime)) {
    const t = nowTime();
    document.getElementById('now').textContent = fmt(t);
    cursor.style.left = Math.min(100, t / D.duration * 100) + '%';
    let idx = -1; for (let i = 0; i < D.segments.length; i++) if (D.segments[i].start <= t) idx = i;
    if (idx >= 0 && D.segments[idx].end + 0.6 < t) idx = -1;
    if (idx !== lastActive) {
      if (lastActive >= 0) { trs[lastActive].classList.remove('active'); tlSegs[lastActive].classList.remove('active'); }
      if (idx >= 0) { trs[idx].classList.add('active'); tlSegs[idx].classList.add('active');
        const r = trs[idx]; const top = r.offsetTop - wrap.clientHeight/2 + r.clientHeight/2; wrap.scrollTo({ top, behavior: 'smooth' }); }
      lastActive = idx;
    }
  }
}
setInterval(tick, 100);

/* ---------- Chinese reading (Kokoro, per-word timing) ---------- */
const sents = document.getElementById('sents');
const audios = D.first3.map(s => { const a = new Audio('data:audio/mpeg;base64,' + s.audio); a.preload = 'auto'; return a; });
let current = null, timer = null, queue = null, rate = 1;
const sentEls = D.first3.map((s, i) => {
  const el = document.createElement('div'); el.className = 'sent'; el.id = 'sent' + i;
  el.innerHTML = `<div class="src">${fmt(s.start)}–${fmt(s.end)} · ${esc(s.text)}</div><div class="row"><div class="words"></div>
    <div class="btns"><button class="play" data-r="1">▶ เล่น</button><button class="play" data-r="0.7">🐢 0.7x</button><span class="time">${s.audio_duration.toFixed(1)}s</span></div></div>`;
  const wc = el.querySelector('.words');
  s.words.forEach((w, j) => {
    const d = document.createElement('div'); d.className = 'w' + (w.end > w.start ? '' : ' punct');
    d.innerHTML = `<span class="han">${esc(w.word)}</span><span class="py">${esc(w.pinyin || ' ')}</span>`;
    if (w.end > w.start) d.onclick = () => playWord(i, j);
    wc.appendChild(d);
  });
  el.querySelectorAll('button').forEach(b => b.onclick = () => playSentence(i, +b.dataset.r));
  sents.appendChild(el); return el;
});
function stopAll() {
  if (current !== null) { audios[current].pause(); audios[current].onended = null; clearHL(current); sentEls[current].classList.remove('playing'); }
  current = null; queue = null; if (timer) { clearInterval(timer); timer = null; }
  document.getElementById('playAll').classList.remove('on'); document.getElementById('playAllSlow').classList.remove('on');
}
function clearHL(i) { sentEls[i].querySelectorAll('.w').forEach(w => w.classList.remove('hl', 'done')); }
function playSentence(i, r, from = 0, until = null) {
  stopAll(); pauseVideo(); current = i; rate = r;
  const a = audios[i], el = sentEls[i], ws = el.querySelectorAll('.w'), words = D.first3[i].words;
  el.classList.add('playing'); el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  a.playbackRate = r; a.currentTime = from; a.play();
  const step = () => {
    const t = a.currentTime;
    if (until !== null && t >= until) { a.pause(); a.onended(); return; }
    words.forEach((w, j) => { const on = t >= w.start && t < w.end; ws[j].classList.toggle('hl', on && w.end > w.start); ws[j].classList.toggle('done', t >= w.end && w.end > w.start); });
  };
  timer = setInterval(step, 40); step();
  a.onended = () => { clearInterval(timer); timer = null; clearHL(i); el.classList.remove('playing'); current = null;
    if (queue && queue.length) { const n = queue.shift(); playSentenceKeepQueue(n, rate); } else { queue = null; document.getElementById('playAll').classList.remove('on'); document.getElementById('playAllSlow').classList.remove('on'); } };
}
function playSentenceKeepQueue(i, r) { const q = queue; playSentence(i, r); queue = q; }
function playWord(i, j) { const w = D.first3[i].words[j]; playSentence(i, 1, Math.max(0, w.start - 0.02), w.end + 0.02); }
function playAll(r) { const ids = D.first3.map((_, i) => i); stopAll(); queue = ids.slice(1); playSentenceKeepQueue(ids[0], r);
  document.getElementById(r === 1 ? 'playAll' : 'playAllSlow').classList.add('on'); }
document.getElementById('playAll').onclick = () => playAll(1);
document.getElementById('playAllSlow').onclick = () => playAll(0.7);
document.getElementById('stopAll').onclick = stopAll;
</script>
</body>
</html>
"""
html = HTML.replace("__TITLE__", data["title"].replace("<", "&lt;")).replace("__DATA__", payload)
dst.write_text(html, encoding="utf-8")
print("wrote", dst, dst.stat().st_size // 1024, "KB")
