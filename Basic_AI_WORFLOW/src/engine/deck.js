/* Offline deck: navigation and reusable components only. */
(() => {
  'use strict';
  const slots = [...document.querySelectorAll('#stage > .slot')];
  let index = 0;
  const overview = () => document.body.classList.contains('overview');
  const fit = () => document.documentElement.style.setProperty('--s', Math.min(innerWidth / 1280, innerHeight / 720));
  function show(n, sync = true) {
    index = Math.max(0, Math.min(slots.length - 1, n));
    slots.forEach((slot, i) => { slot.classList.toggle('active', i === index); slot.setAttribute('aria-hidden', String(!overview() && i !== index)); });
    document.querySelector('#counter').textContent = `${index + 1} / ${slots.length}`;
    document.querySelector('#progress i').style.width = `${(index + 1) / slots.length * 100}%`;
    if (sync && location.hash !== `#p${index + 1}`) history.replaceState(null, '', `#p${index + 1}`);
  }
  function toggleOverview(value = !overview()) {
    document.body.classList.toggle('overview', value);
    document.querySelector('#overview').setAttribute('aria-pressed', String(value));
    show(index); if (!value) scrollTo(0, 0);
  }
  function interactive(target) {
    if (!(target instanceof Element)) return false;
    if (target.closest('iframe,.copybox,.tabs,.ui-frame,.mdbox,.trace,.figure,.figure-overlay,button,a,input,select,textarea,[contenteditable]:not([contenteditable="false"])')) return true;
    for (let el = target; el && el !== document.body; el = el.parentElement) {
      const css = getComputedStyle(el);
      if (/(auto|scroll)/.test(css.overflow + css.overflowX + css.overflowY) && (el.scrollHeight > el.clientHeight || el.scrollWidth > el.clientWidth)) return true;
    }
    return false;
  }
  let lastFigureButton = null;
  function closeFigure() {
    document.querySelector('.figure-overlay')?.remove();
    lastFigureButton?.focus(); lastFigureButton = null;
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { if (document.querySelector('.figure-overlay')) closeFigure(); else if (overview()) toggleOverview(false); return; }
    if (e.ctrlKey || e.metaKey || e.altKey || interactive(e.target) || document.querySelector('.figure-overlay')) return;
    const moves = {ArrowRight: 1, ' ': 1, PageDown: 1, ArrowLeft: -1, PageUp: -1};
    if (e.key in moves) { e.preventDefault(); if (!overview()) show(index + moves[e.key]); }
    else if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); toggleOverview(false); show(e.key === 'Home' ? 0 : slots.length - 1); }
    else if (e.key.toLowerCase() === 'o') { e.preventDefault(); toggleOverview(); }
  });
  document.querySelector('#stage').addEventListener('click', e => {
    const slot = e.target.closest('.slot');
    if (overview() && slot) { show(slots.indexOf(slot)); toggleOverview(false); return; }
    if (interactive(e.target)) return;
    const rect = slots[index].getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    if (x >= 0 && x < .25) show(index - 1);
    else if (x > .75 && x <= 1) show(index + 1);
  });
  document.querySelector('#prev').onclick = e => { show(index - 1); e.currentTarget.blur(); };
  document.querySelector('#next').onclick = e => { show(index + 1); e.currentTarget.blur(); };
  document.querySelector('#overview').onclick = e => { toggleOverview(); e.currentTarget.blur(); };
  document.querySelectorAll('[data-goto]').forEach(button => button.addEventListener('click', () => { toggleOverview(false); show(Number(button.dataset.goto) - 1); button.blur(); }));
  document.querySelectorAll('.copybox').forEach(box => {
    const button = box.querySelector('button.copy'), pre = box.querySelector('pre');
    if (!button || !pre) return;
    let timer;
    button.addEventListener('click', async () => {
      let copied = false;
      try { await navigator.clipboard.writeText(pre.textContent); copied = true; } catch (_) {
        const input = document.createElement('textarea'); input.value = pre.textContent;
        input.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.append(input); input.select();
        try { copied = document.execCommand('copy'); } finally { input.remove(); button.focus(); }
      }
      clearTimeout(timer); button.textContent = copied ? 'Copied' : 'คัดลอกไม่สำเร็จ';
      timer = setTimeout(() => { button.textContent = 'Copy'; }, 1200);
    });
  });
  document.querySelectorAll('.tabs').forEach((tabs, ti) => {
    const bar = tabs.querySelector(':scope > .tabbar'); if (!bar) return;
    const buttons = [...bar.querySelectorAll('button[data-tab]')];
    const panes = [...tabs.querySelectorAll(':scope > .tabpane[data-tab]')];
    bar.setAttribute('role', 'tablist');
    function select(button) {
      buttons.forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-selected', String(b === button)); });
      panes.forEach(p => { p.hidden = p.dataset.tab !== button.dataset.tab; p.classList.toggle('active', !p.hidden); });
    }
    buttons.forEach((button, bi) => {
      button.type = 'button'; button.setAttribute('role', 'tab'); button.id ||= `tab-${ti}-${bi}`;
      const pane = panes.find(p => p.dataset.tab === button.dataset.tab);
      if (pane) { pane.id ||= `pane-${ti}-${bi}`; pane.setAttribute('role', 'tabpanel'); pane.setAttribute('aria-labelledby', button.id); button.setAttribute('aria-controls', pane.id); }
      button.addEventListener('click', () => select(button));
    });
    if (buttons.length) select(buttons[0]);
  });
  document.querySelectorAll('.ui-frame').forEach(frame => {
    const iframe = frame.querySelector('iframe'); if (!iframe) return;
    iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-modals');
    const toolbar = document.createElement('div'); toolbar.className = 'frame-tools';
    const open = document.createElement('button'), reload = document.createElement('button');
    open.textContent = 'เปิดเต็มหน้าต่าง'; reload.textContent = 'โหลดใหม่';
    open.onclick = () => {
      const url = URL.createObjectURL(new Blob([iframe.srcdoc], {type: 'text/html;charset=utf-8'}));
      window.open(url, '_blank', 'noopener'); setTimeout(() => URL.revokeObjectURL(url), 60000);
    };
    reload.onclick = () => { const source = iframe.srcdoc; iframe.srcdoc = source; };
    toolbar.append(open, reload); frame.append(toolbar);
  });
  document.querySelectorAll('figure.figure').forEach(figure => {
    const visual = figure.querySelector('svg,img'); if (!visual) return;
    const button = document.createElement('button'); button.textContent = 'ขยายภาพ'; button.type = 'button'; figure.append(button);
    button.onclick = () => {
      closeFigure(); lastFigureButton = button;
      const overlay = document.createElement('div'); overlay.className = 'figure-overlay'; overlay.setAttribute('role', 'dialog'); overlay.setAttribute('aria-modal', 'true'); overlay.setAttribute('aria-label', 'ภาพขยาย');
      const close = document.createElement('button'); close.textContent = 'ปิดภาพ (Esc)';
      overlay.append(visual.cloneNode(true), close); overlay.onclick = closeFigure; document.body.append(overlay); close.focus();
    };
  });
  function fromHash() { const m = location.hash.match(/^#p(\d+)$/); show(m ? Number(m[1]) - 1 : 0); }
  window.addEventListener('hashchange', fromHash); window.addEventListener('resize', fit);
  fit(); fromHash(); document.documentElement.dataset.deckReady = 'true';
})();
