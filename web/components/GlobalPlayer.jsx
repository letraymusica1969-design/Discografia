'use client';

import { useEffect, useRef, useState } from 'react';
import { useAudio } from './AudioProvider';
import { COVER_VERSION } from '../lib/version';

const fmt = (s) => {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60);
  return `${m}:${String(ss).padStart(2, '0')}`;
};

const seekFrom = (e) => {
  const r = e.currentTarget.getBoundingClientRect();
  return Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1);
};

export default function GlobalPlayer() {
  const { now, playing, time, dur, muted, toggle, seekFrac, skip, toggleMute, stop, play } = useAudio();
  const [scrollMini, setScrollMini] = useState(false);
  const [hover, setHover] = useState(false);
  const [forced, setForced] = useState(false);
  const [full, setFull] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const swipe = useRef(null);

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 700px)');
    const up = () => setIsMobile(mq.matches);
    up();
    mq.addEventListener('change', up);
    return () => mq.removeEventListener('change', up);
  }, []);

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

  useEffect(() => {
    document.documentElement.style.overflow = full ? 'hidden' : '';
    return () => {
      document.documentElement.style.overflow = '';
    };
  }, [full]);

  useEffect(() => {
    document.body.classList.toggle('has-player', !!now);
    return () => document.body.classList.remove('has-player');
  }, [now]);

  if (!now) return null;
  const pct = dur > 0 ? (time / dur) * 100 : 0;
  const n = String(now.track.n).padStart(2, '0');
  const mini = forced || (scrollMini && !hover);
  const t = now.track;
  const tracks = now.meta.tracks || [];

  const onNpDown = (e) => {
    swipe.current = { x: e.clientX, y: e.clientY };
  };
  const onNpUp = (e) => {
    if (swipe.current && e.clientY - swipe.current.y > 90) setFull(false);
    swipe.current = null;
  };

  return (
    <>
      <div className={'gp-halo' + (playing ? ' is-playing' : '')} aria-hidden />
      <div
        className={'gp' + (playing ? ' is-playing' : '') + (mini ? ' is-mini' : '') + (isMobile ? ' is-touch' : '')}
        role="region"
        aria-label="Reproductor"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
      >
        <div
          className="gp-line"
          onClick={(e) => seekFrac(seekFrom(e))}
        >
          <div className="gp-line-fill" style={{ width: `${pct}%` }} />
        </div>
        <div
          className="gp-in"
          onClick={(e) => {
            if (e.target.closest('button')) return;
            if (isMobile) setFull(true);
          }}
        >
          <span className="gp-grip" aria-hidden />
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
              onClick={(e) => seekFrac(seekFrom(e))}
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
              className={'gp-btn sm vol' + (muted ? ' is-off' : '')}
              onClick={toggleMute}
              aria-pressed={muted}
              aria-label={muted ? 'Activar sonido' : 'Silenciar'}
              title={muted ? 'Activar sonido' : 'Silenciar'}
            >
              ♪
            </button>
            <button
              className="gp-btn sm close"
              onClick={stop}
              aria-label="Cerrar reproductor"
              title="Cerrar"
            >
              ✕
            </button>
            {!isMobile && (
              <button
                className="gp-btn mini-toggle"
                onClick={() => setForced((m) => !m)}
                aria-label={mini ? 'Expandir reproductor' : 'Minimizar reproductor'}
                title={mini ? 'Expandir' : 'Minimizar'}
              >
                {mini ? '⌃' : '⌄'}
              </button>
            )}
          </div>
        </div>
      </div>

      {isMobile && full && (
        <div
          className="np"
          role="dialog"
          aria-modal="true"
          aria-label="Reproductor full screen"
        >
          <div className="np-top">
            <button className="np-dismiss" onClick={() => setFull(false)} aria-label="Minimizar reproductor">
              ⌄
            </button>
            <span className="np-now">REPRODUCIENDO</span>
            <button className="np-x" onClick={stop} aria-label="Cerrar reproductor">
              ✕
            </button>
          </div>

          <div className="np-stage" onPointerDown={onNpDown} onPointerUp={onNpUp}>
            <div className={'np-halo' + (playing ? ' on' : '')} aria-hidden />
            <div className={'np-disk' + (playing ? ' is-playing' : '')}>
              <img
                src={`/covers/${now.meta.slug}_front.jpg?${COVER_VERSION}`}
                alt={`${now.meta.titulo} — ahora sonando`}
                draggable="false"
              />
              <span className="np-sheen" aria-hidden />
              <span className="np-ring" aria-hidden />
            </div>
          </div>

          <div className="np-meta">
            <h2>{t.titulo}</h2>
            <p className="np-album">
              {now.meta.titulo} · PISTA {n}
            </p>
            <p className="np-feats">
              {t.bpm ? `${t.bpm.toFixed ? t.bpm.toFixed(0) : t.bpm} BPM` : ''}
              {t.bpm && t.tonalidad ? ' · ' : ''}
              {t.tonalidad || ''}
            </p>
          </div>

          <div className="np-prog">
            <div className="gp-bar np-bar" onClick={(e) => seekFrac(seekFrom(e))}>
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

          <div className="np-ctr">
            <button className="np-btn" onClick={() => skip(-1)} aria-label="Anterior">
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                <path d="M6 5h2.4v14H6zM8.6 12 20 5v14z" />
              </svg>
            </button>
            <button className="np-btn big" onClick={toggle} aria-label="Play / Pausa">
              {playing ? (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                  <rect x="6" y="4.5" width="4.4" height="15" rx="1.4" />
                  <rect x="13.6" y="4.5" width="4.4" height="15" rx="1.4" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                  <path d="M7.5 4.5 20 12 7.5 19.5z" />
                </svg>
              )}
            </button>
            <button className="np-btn" onClick={() => skip(1)} aria-label="Siguiente">
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                <path d="M15.6 5H18v14h-2.4zM15.4 12 4 5v14z" />
              </svg>
            </button>
          </div>

          <div className="np-aux">
            <button
              className={'np-chip' + (muted ? ' off' : '')}
              onClick={toggleMute}
              aria-pressed={muted}
              aria-label={muted ? 'Activar sonido' : 'Silenciar'}
            >
              ♪
            </button>
          </div>

          {tracks.length > 0 && (
            <div className="np-songs">
              <p className="np-songs-lbl">DEL MISMO DISCO</p>
              {tracks.map((tr, i) => {
                const on = now.meta.slug === now.meta.slug && tr.n === t.n;
                return (
                  <button
                    key={tr.n}
                    className={'np-song' + (on ? ' is-on' : '')}
                    onClick={() => (on ? toggle() : play(tracks, now.meta, i))}
                  >
                    <span className="np-song-n">{String(tr.n).padStart(2, '0')}</span>
                    <span className="np-song-t">{tr.titulo}</span>
                    <span className={'np-song-meta'}>
                      {fmt(tr.duracion)}
                      {tr.bpm ? ` · ${tr.bpm.toFixed ? tr.bpm.toFixed(0) : tr.bpm} BPM` : ''}
                    </span>
                    {on && (
                      <span className={'eq' + (playing ? ' is-play' : '')} aria-hidden>
                        <i style={{ animationDelay: '0s' }} />
                        <i style={{ animationDelay: '0.18s' }} />
                        <i style={{ animationDelay: '0.36s' }} />
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}
    </>
  );
}