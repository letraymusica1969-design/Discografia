'use client';

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
  if (!now) return null;
  const pct = dur > 0 ? (time / dur) * 100 : 0;
  const n = String(now.track.n).padStart(2, '0');
  return (
    <div className={'gp' + (playing ? ' is-playing' : '')} role="region" aria-label="Reproductor">
      <div className="gp-halo" />
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
            <span className="gp-tt">{now.track.titulo}</span>
            <span className="gp-lbl">PISTA {n}</span>
          </div>
          <div className="gp-sub">{now.meta.titulo}</div>
          <div className="gp-bar" onClick={(e) => {
            const r = e.currentTarget.getBoundingClientRect();
            seekFrac(Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1));
          }}>
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
        </div>
      </div>
    </div>
  );
}