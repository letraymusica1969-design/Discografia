'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';

const AudioCtx = createContext(null);

export const useAudio = () => useContext(AudioCtx);

export default function AudioProvider({ children }) {
  const audioRef = useRef(null);
  const listRef = useRef([]);
  const metaRef = useRef({ slug: '', titulo: '' });
  const idxRef = useRef(-1);
  const nowRef = useRef(null);
  const [now, setNow] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [dur, setDur] = useState(0);
  nowRef.current = now;

  const loadAndPlay = (list, meta, i) => {
    const t = list[i];
    if (!t || !t.audio) return;
    listRef.current = list;
    metaRef.current = meta;
    idxRef.current = i;
    const a = audioRef.current;
    a.src = t.audio;
    setNow({ track: t, meta });
    setTime(0);
    setDur(0);
    a.play();
  };

  useEffect(() => {
    const a = new Audio();
    a.preload = 'none';
    audioRef.current = a;
    const onTime = () => setTime(a.currentTime);
    const onMeta = () => setDur(a.duration || 0);
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    const onEnd = () => {
      if (idxRef.current + 1 < listRef.current.length) {
        loadAndPlay(listRef.current, metaRef.current, idxRef.current + 1);
      } else {
        setPlaying(false);
        setTime(0);
      }
    };
    const onError = () => setPlaying(false);
    a.addEventListener('timeupdate', onTime);
    a.addEventListener('loadedmetadata', onMeta);
    a.addEventListener('play', onPlay);
    a.addEventListener('pause', onPause);
    a.addEventListener('ended', onEnd);
    a.addEventListener('error', onError);
    return () => {
      a.pause();
      a.removeEventListener('timeupdate', onTime);
      a.removeEventListener('loadedmetadata', onMeta);
      a.removeEventListener('play', onPlay);
      a.removeEventListener('pause', onPause);
      a.removeEventListener('ended', onEnd);
      a.removeEventListener('error', onError);
    };
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (!nowRef.current) return;
      const tag = e.target && e.target.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if (e.code === 'Space') {
        e.preventDefault();
        const a = audioRef.current;
        if (a) (a.paused ? a.play() : a.pause());
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        const a = audioRef.current;
        if (a) a.currentTime = Math.min(a.duration || dur, a.currentTime + 5);
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        const a = audioRef.current;
        if (a) a.currentTime = Math.max(0, a.currentTime - 5);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [dur]);

  const play = (list, meta, i) => loadAndPlay(list, meta, i);

  const toggle = () => {
    const a = audioRef.current;
    if (!a || !nowRef.current) return;
    if (a.paused) a.play(); else a.pause();
  };

  const seekFrac = (f) => {
    const a = audioRef.current;
    if (!a || !nowRef.current || !isFinite(dur) || dur <= 0) return;
    a.currentTime = f * dur;
    setTime(a.currentTime);
  };

  const skip = (dir) => {
    const i = idxRef.current + dir;
    if (i >= 0 && i < listRef.current.length) {
      loadAndPlay(listRef.current, metaRef.current, i);
    }
  };

  return (
    <AudioCtx.Provider value={{ now, playing, time, dur, play, toggle, seekFrac, skip }}>
      {children}
    </AudioCtx.Provider>
  );
}