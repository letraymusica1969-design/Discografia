'use client';

import { useAudio } from './AudioProvider';

const fmtDur = (s) => {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60);
  return `${m}:${String(ss).padStart(2, '0')}`;
};

export default function DiscoPlayer({ tracks, slug, titulo }) {
  const { now, playing, toggle, play } = useAudio();
  const meta = { slug, titulo };
  return (
    <ol className="page-disco-tracks tp-list">
      {tracks.map((t, i) => {
        const active = !!now && now.meta.slug === slug && now.track.n === t.n;
        return (
          <li key={t.n} className={'tp-track' + (active ? ' is-on' : '')}>
            <div
              className="t-row tp-row"
              onClick={() => (active ? toggle() : play(tracks, meta, i))}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  active ? toggle() : play(tracks, meta, i);
                }
              }}
            >
              <span className="t-n tp-n">
                {active ? (
                  <span className={'eq' + (playing ? ' is-play' : '')} aria-hidden>
                    <i style={{ animationDelay: '0s' }} />
                    <i style={{ animationDelay: '0.18s' }} />
                    <i style={{ animationDelay: '0.36s' }} />
                  </span>
                ) : (
                  String(t.n).padStart(2, '0')
                )}
              </span>
              <span className="t-t">{t.titulo}</span>
              <span className="t-bpm">
                {active ? (playing ? 'SONANDO' : 'PAUSA') : t.bpm ? `${t.bpm.toFixed(0)} BPM` : ''}
              </span>
              <span className="t-d">{fmtDur(t.duracion)}</span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}