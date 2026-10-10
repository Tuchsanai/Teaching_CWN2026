"use client";

import { useEffect, useRef, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

// FR-34 เพลงสปาเปิดด้วยปุ่มเท่านั้น (ไม่มี autoplay NFR-08) · สร้างเสียงเองด้วย Web Audio API ไม่โหลดไฟล์จากเน็ต
// คอร์ดเพนทาโทนิกช้า ๆ + เสียงระฆังตามลำดับตายตัว
const PAD = [220, 261.63, 329.63, 392];
const BELLS = [659.25, 587.33, 523.25, 440, 523.25, 587.33, 783.99, 659.25];

export function MusicToggle() {
  const { t } = useI18n();
  const [playing, setPlaying] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);
  const stopRef = useRef<(() => void) | null>(null);

  useEffect(() => () => stopRef.current?.(), []);

  const start = () => {
    const AC = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = ctxRef.current ?? new AC();
    ctxRef.current = ctx;
    void ctx.resume();
    const master = ctx.createGain();
    master.gain.setValueAtTime(0, ctx.currentTime);
    master.gain.linearRampToValueAtTime(0.18, ctx.currentTime + 2);
    master.connect(ctx.destination);

    const oscs: OscillatorNode[] = [];
    PAD.forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "sine";
      o.frequency.value = f;
      g.gain.value = 0.12 / (i + 1);
      const lfo = ctx.createOscillator();
      const lg = ctx.createGain();
      lfo.frequency.value = 0.07 + i * 0.03;
      lg.gain.value = 0.05;
      lfo.connect(lg).connect(g.gain);
      o.connect(g).connect(master);
      o.start();
      lfo.start();
      oscs.push(o, lfo);
    });

    let step = 0;
    const bell = () => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "triangle";
      o.frequency.value = BELLS[step % BELLS.length];
      step++;
      const now = ctx.currentTime;
      g.gain.setValueAtTime(0.0001, now);
      g.gain.exponentialRampToValueAtTime(0.25, now + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, now + 3.5);
      o.connect(g).connect(master);
      o.start(now);
      o.stop(now + 3.6);
    };
    bell();
    const timer = window.setInterval(bell, 2600);

    stopRef.current = () => {
      window.clearInterval(timer);
      const now = ctx.currentTime;
      master.gain.cancelScheduledValues(now);
      master.gain.setValueAtTime(master.gain.value, now);
      master.gain.linearRampToValueAtTime(0, now + 0.4);
      oscs.forEach((o) => o.stop(now + 0.5));
      window.setTimeout(() => master.disconnect(), 600);
      stopRef.current = null;
    };
  };

  const toggle = () => {
    if (playing) {
      stopRef.current?.();
      setPlaying(false);
    } else {
      start();
      setPlaying(true);
    }
  };

  return (
    <button
      type="button"
      className={`music-btn${playing ? " on" : ""}`}
      onClick={toggle}
      aria-pressed={playing}
      data-testid="music-toggle"
      data-playing={playing ? "true" : "false"}
    >
      <span aria-hidden="true">{playing ? "♫" : "♪"}</span> <span className="music-label">{playing ? t("music.stop") : t("music.play")}</span>
    </button>
  );
}
