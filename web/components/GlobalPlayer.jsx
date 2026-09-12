'use client';

import { useEffect, useState } from 'react';
import { useAudio } from './AudioProvider';
import { COVER_VERSION } from '../lib/version';

const fmt = (s) => {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60);
  return `${m}:${String(ss).padStart(2, '0')}`;
};

export default function GlobalPlayer() {
  const { now, playing, time, dur, toggle, seekFrac, skip } = useAudio();
  const [scrollMini, setScrollMini] = useState(false);
  const [hover, setHover] = useState(false);
  const [forced, setForced] = useState(false);

  useEffect(() => {
    if (!now) return;
    let lastY = window.scrollY;
    const onScroll = () => {
      const y = window.scrollY;
      setScrollMini(y > 160 && y >= lastY);
      if (y < 60) setForced(false);
      lastY = y;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [now]);

  if (!now) return null;
  const pct = dur > 0 ? (time / dur) * 100 : 0;
  const n = String(now.track.n).padStart(2, '0');
  const mini = forced || (scrollMini && !hover);
  const t = now.track;

  return (
    <>
      <div className={'gp-halo' + (playing ? ' is-playing' : '')} aria-hidden />
      <div
        className={'gp' + (playing ? ' is-playing' : '') + (mini ? ' is-mini' : '')}
        role="region"
        aria-label="Reproductor"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
      >
        <div
          className="gp-line"
          onClick={(e) => {
            const r = e.currentTarget.getBoundingClientRect();
            seekFrac(Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1));
          }}
        >
          <div className="gp-line-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="gp-in">
          <div className="gp-thumb">
            <img
              src={`/covers/${now.meta.slug}_front.jpg?${COVER_VERSION}`}
              alt=""
              draggable="false"
            />
            <span className={'gp-eq' + (playing ? ' is-play' : '')} aria-hidden>
              <i />
              <i />
              <i />
            </span>
          </div>
          <div className="gp-mid">
            <div className="gp-title-row">
              <span className="gp-tt">{t.titulo}</span>
              <span className="gp-lbl">PISTA {n}</span>
            </div>
            <div className="gp-sub">
              {now.meta.titulo}
              {t.bpm ? ` · ${t.bpm.toFixed ? t.bpm.toFixed(0) : t.bpm} BPM` : ''}
              {t.tonalidad ? ` · ${t.tonalidad}` : ''}
            </div>
            <div
              className="gp-bar"
              onClick={(e) => {
                const r = e.currentTarget.getBoundingClientRect();
                seekFrac(Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1));
              }}
            >
              <div className="gp-fill" style={{ width: `${pct}%` }}>
                <span className="gp-thumb-dot" />
              </div>
              <span className="gp-shine" />
            </div>
            <div className="gp-times">
              <span>{fmt(time)}</span>
              <span>{fmt(dur)}</span>
            </div>
          </div>
          <div className="gp-ctr">
            <button className="gp-btn sm" onClick={() => skip(-1)} aria-label="Anterior">
              ⏮
            </button>
            <button className="gp-btn play" onClick={toggle} aria-label="Play / Pausa">
              {playing ? '❚❚' : '▶'}
            </button>
            <button className="gp-btn sm" onClick={() => skip(1)} aria-label="Siguiente">
              ⏭
            </button>
            <button
              className="gp-btn mini-toggle"
              onClick={() => setForced((m) => !m)}
              aria-label={mini ? 'Expandir reproductor' : 'Minimizar reproductor'}
              title={mini ? 'Expandir' : 'Minimizar'}
            >
              {mini ? '⌃' : '⌄'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}