'use client';

import { useEffect, useRef, useState } from 'react';

const fmt = (s) => {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const ss = Math.floor(s % 60);
  return `${m}:${String(ss).padStart(2, '0')}`;
};

export default function DiscoPlayer({ tracks }) {
  const audioRef = useRef(null);
  const [cur, setCur] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [dur, setDur] = useState(0);

  useEffect(() => {
    const a = new Audio();
    a.preload = 'none';
    audioRef.current = a;
    const onTime = () => setTime(a.currentTime);
    const onMeta = () => setDur(a.duration || 0);
    const onPlay = () => setPlaying(true);
    const onPause = () => { setPlaying(false); };
    const onEnd = () => { setPlaying(false); setTime(0); setDur(0); setCur(0); };
    a.addEventListener('timeupdate', onTime);
    a.addEventListener('loadedmetadata', onMeta);
    a.addEventListener('play', onPlay);
    a.addEventListener('pause', onPause);
    a.addEventListener('ended', onEnd);
    return () => {
      a.pause();
      a.removeEventListener('timeupdate', onTime);
      a.removeEventListener('loadedmetadata', onMeta);
      a.removeEventListener('play', onPlay);
      a.removeEventListener('pause', onPause);
      a.removeEventListener('ended', onEnd);
    };
  }, []);

  const toggle = (t) => {
    const a = audioRef.current;
    if (!a) return;
    if (cur === t.n) {
      if (playing) { a.pause(); } else { a.play(); }
      return;
    }
    a.src = t.audio;
    setCur(t.n);
    setTime(0);
    setDur(0);
    a.play();
  };

  const seek = (e) => {
    const a = audioRef.current;
    if (!a || !cur || !isFinite(dur)) return;
    const r = e.currentTarget.getBoundingClientRect();
    const f = Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1);
    a.currentTime = f * dur;
    setTime(a.currentTime);
  };

  const pct = isFinite(dur) && dur > 0 ? (time / dur) * 100 : 0;

  return (
    <ol className="page-disco-tracks tp-list">
      {tracks.map((t) => {
        const active = cur === t.n;
        return (
          <li key={t.n} className={'tp-track' + (active ? ' is-on' : '')}>
            <div className="t-row tp-row" onClick={() => toggle(t)} role="button"
              tabIndex={0} onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggle(t); }}>
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
              <span className="t-bpm">{t.bpm ? `${t.bpm.toFixed(0)} BPM` : ''}</span>
              <span className="t-d">{fmt(t.duracion)}</span>
            </div>

            {active && (
              <div className="tp-player">
                <div className="tp-bar" onClick={seek}>
                  <div className="tp-fill" style={{ width: `${pct}%` }}>
                    <span className="tp-thumb" />
                  </div>
                  <span className="tp-shine" />
                </div>
                <div className="tp-left">
                  <button className="tp-btn" onClick={(e) => { e.stopPropagation(); toggle(t); }}
                    aria-label={playing ? 'Pausar' : 'Reproducir'}>
                    {playing ? '❚❚' : '▶'}
                  </button>
                  <span className="tp-time">{fmt(time)} / {fmt(dur)}</span>
                </div>
              </div>
            )}
          </li>
        );
      })}
    </ol>
  );
}