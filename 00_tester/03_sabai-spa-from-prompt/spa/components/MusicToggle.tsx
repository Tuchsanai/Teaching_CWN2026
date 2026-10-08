"use client";

import { useEffect, useRef, useState } from "react";
import { useApp } from "./AppProvider";
import { Icon } from "./Ornament";

// FR-24 / NFR-09: ambient spa music generated with the Web Audio API.
// Nothing is created until the visitor presses the button — never autoplays.

const PENTATONIC = [440, 523.25, 587.33, 659.25, 783.99, 880, 659.25, 587.33]; // A minor pentatonic
const MELODY = [0, 2, 4, 3, 5, 4, 2, 1, 0, 3, 2, 6, 4, 2, 1, 0]; // fixed order — no randomness

type Engine = { ctx: AudioContext; master: GainNode; timer: number; nodes: AudioNode[] };

function startEngine(): Engine {
  const Ctor = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
  const ctx = new Ctor();
  const master = ctx.createGain();
  master.gain.value = 0;
  master.gain.linearRampToValueAtTime(0.16, ctx.currentTime + 2.5);

  // soft echo for a spacious feel
  const delay = ctx.createDelay(2);
  delay.delayTime.value = 0.42;
  const fb = ctx.createGain();
  fb.gain.value = 0.35;
  const lp = ctx.createBiquadFilter();
  lp.type = "lowpass";
  lp.frequency.value = 1800;
  delay.connect(fb).connect(lp).connect(delay);
  lp.connect(master);
  master.connect(ctx.destination);

  // warm drone (A2 + E3 + A3) with a slow breathing LFO
  const nodes: AudioNode[] = [];
  const droneGain = ctx.createGain();
  droneGain.gain.value = 0.22;
  const droneFilter = ctx.createBiquadFilter();
  droneFilter.type = "lowpass";
  droneFilter.frequency.value = 600;
  droneGain.connect(droneFilter).connect(master);
  for (const [f, detune] of [[110, -4], [164.81, 3], [220, 0]] as const) {
    const o = ctx.createOscillator();
    o.type = "sine";
    o.frequency.value = f;
    o.detune.value = detune;
    o.connect(droneGain);
    o.start();
    nodes.push(o);
  }
  const lfo = ctx.createOscillator();
  lfo.frequency.value = 0.08;
  const lfoGain = ctx.createGain();
  lfoGain.gain.value = 0.08;
  lfo.connect(lfoGain).connect(droneGain.gain);
  lfo.start();
  nodes.push(lfo);

  // gentle bell melody (khim-like) on a fixed sequence
  let step = 0;
  const bell = () => {
    const t = ctx.currentTime + 0.05;
    const f = PENTATONIC[MELODY[step % MELODY.length]];
    step++;
    for (const [mult, vol] of [[1, 0.12], [2.01, 0.03], [3.02, 0.012]] as const) {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "sine";
      o.frequency.value = f * mult;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 3.2);
      o.connect(g);
      g.connect(master);
      g.connect(delay);
      o.start(t);
      o.stop(t + 3.3);
    }
  };
  bell();
  const timer = window.setInterval(bell, 1800);
  return { ctx, master, timer, nodes };
}

function stopEngine(e: Engine) {
  window.clearInterval(e.timer);
  const t = e.ctx.currentTime;
  e.master.gain.cancelScheduledValues(t);
  e.master.gain.setValueAtTime(e.master.gain.value, t);
  e.master.gain.linearRampToValueAtTime(0, t + 0.6);
  window.setTimeout(() => e.ctx.close().catch(() => undefined), 700);
}

export function MusicToggle() {
  const { t } = useApp();
  const [on, setOn] = useState(false);
  const eng = useRef<Engine | null>(null);

  useEffect(() => () => {
    if (eng.current) stopEngine(eng.current);
  }, []);

  const toggle = () => {
    if (on) {
      if (eng.current) stopEngine(eng.current);
      eng.current = null;
      setOn(false);
    } else {
      try {
        eng.current = startEngine();
        setOn(true);
      } catch {
        setOn(false);
      }
    }
  };

  return (
    <button
      type="button"
      className={`icon-btn music-btn ${on ? "is-on" : ""}`}
      onClick={toggle}
      aria-pressed={on}
      aria-label={on ? t("music_stop") : t("music_play")}
      title={on ? t("music_stop") : t("music_play")}
      data-testid="music-toggle"
      data-playing={on ? "true" : "false"}
    >
      <Icon name={on ? "music" : "music-off"} />
      <span className="music-bars" aria-hidden="true">
        <i /><i /><i />
      </span>
    </button>
  );
}
