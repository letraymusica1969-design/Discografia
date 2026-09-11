'use client';

import Link from 'next/link';
import { COVER_VERSION } from '../lib/version';

const ACCENT = {
  Medianoche: '#c8a96a',
  'Ciudad de Neon': '#00d9ff',
  Ochentas: '#ff9e4d',
  Llamas: '#ff5a3c',
  Euforia: '#c9ffd6',
};

export default function DiscCard({ d, index = 0 }) {
  const img = `/covers/${d.slug}_front.jpg?${COVER_VERSION}`;
  const accent = ACCENT[d.titulo] || '#c8a96a';
  return (
    <Link
      href={`/disco/${d.slug}`}
      className="disc-card"
      style={{ '--accent': accent, animationDelay: `${index * 0.09}s` }}
    >
      <div className="disc-media">
        <div className="gh-vinyl" data-label={`VOL.${String(d.numero).padStart(2, '0')}`} aria-hidden />
        <div className="disc-cover">
          <img src={img} alt={`${d.titulo} — portada`} />
        </div>
      </div>
      <div className="disc-meta">
        <p className="disc-year">Box Set · Vinilo · 2026</p>
        <h3>{d.titulo}</h3>
        <p className="disc-sub">{d.subtitulo}</p>
        <p className="disc-num">{d.tracklist.length} canciones · Ver el disco →</p>
      </div>
    </Link>
  );
}