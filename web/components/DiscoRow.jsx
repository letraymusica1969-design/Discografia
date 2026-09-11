'use client';

import { useRef, useState } from 'react';
import Link from 'next/link';
import { COVER_VERSION } from '../lib/version';

const ACCENT = {
  Medianoche: '#c8a96a',
  'Ciudad de Neon': '#00d9ff',
  Ochentas: '#ff9e4d',
  Llamas: '#ff5a3c',
  Euforia: '#c9ffd6',
};

export default function DiscoRow({ d, index = 0 }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const total = d.tracklist.reduce((a, t) => a + t.duracion, 0);
  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const accent = ACCENT[d.titulo] || '#c8a96a';
  const half = Math.ceil(d.tracklist.length / 2);
  const cols = [d.tracklist.slice(0, half), d.tracklist.slice(half)];

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    e.currentTarget.style.setProperty('--mx', `${e.clientX - r.left}px`);
    e.currentTarget.style.setProperty('--my', `${e.clientY - r.top}px`);
  };

  return (
    <article
      className="disco-card"
      ref={ref}
      onMouseMove={onMove}
      style={{ '--accent': accent, animationDelay: `${index * 0.09}s` }}
    >
      <Link href={`/disco/${d.slug}`} className="disco-card-main">
        <div className="disc-media">
          <div className="vinyl" data-label={`VOL.${String(d.numero).padStart(2, '0')}`} aria-hidden />
          <div className="cover"><img src={`/covers/${d.slug}_front.jpg?${COVER_VERSION}`} alt={`${d.titulo} — portada`} /></div>
        </div>
        <div className="disc-info">
          <p className="type">VOL.{String(d.numero).padStart(2, '0')} — BOX SET · VINILO</p>
          <h3>{d.titulo}</h3>
          <p className="sub">{d.subtitulo}</p>
          <p className="stat">{d.tracklist.length} canciones · {fmt(total)}</p>
          <span className="ver">Ver el disco <span>→</span></span>
        </div>
        <div className="ghost" aria-hidden>{String(d.numero).padStart(2, '0')}</div>
      </Link>
      <div className="spotlight" aria-hidden />
      <button className="disco-toggle" onClick={() => setOpen(!open)}>
        {open ? 'Ocultar tracklist' : 'Ver tracklist'}
      </button>
      {open && (
        <div className="tracks">
          {cols.map((col, ci) => (
            <div key={ci}>
              <p className="lado">LADO {ci === 0 ? 'A' : 'B'}</p>
              <ol>
                {col.map((t) => (
                  <li key={t.n}>
                    <span className="t-n">{String(t.n).padStart(2, '0')}</span>
                    <span className="t-t">{t.titulo}</span>
                    <span className="t-bpm">{t.bpm ? `${t.bpm.toFixed(0)} BPM` : ''}</span>
                    <span className="t-d">{fmt(t.duracion)}</span>
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}