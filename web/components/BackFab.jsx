'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

const KEY = 'backfab-pos';

export default function BackFab() {
  const router = useRouter();
  const ref = useRef(null);
  const [pos, setPos] = useState({ right: 26, bottom: 164 });
  const [dragging, setDragging] = useState(false);
  const drag = useRef(null);
  const posRef = useRef(pos);
  posRef.current = pos;

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY));
      if (saved && typeof saved.right === 'number' && typeof saved.bottom === 'number') {
        setPos({ right: saved.right, bottom: saved.bottom });
      }
    } catch {}
  }, []);

  const onDown = (e) => {
    e.preventDefault();
    const r = ref.current.getBoundingClientRect();
    drag.current = { x: e.clientX, y: e.clientY, right: posRef.current.right, bottom: posRef.current.bottom, moved: false };
    e.currentTarget.setPointerCapture(e.pointerId);
    setDragging(true);
  };

  const onMove = (e) => {
    const d = drag.current;
    if (!d) return;
    const dx = e.clientX - d.x;
    const dy = e.clientY - d.y;
    if (!d.moved && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) d.moved = true;
    if (!d.moved) return;
    const btn = ref.current;
    const w = btn.offsetWidth;
    const h = btn.offsetHeight;
    const right = Math.min(Math.max(d.right - dx, 8), window.innerWidth - w - 8);
    const bottom = Math.min(Math.max(d.bottom - dy, 8), window.innerHeight - h - 8);
    setPos({ right, bottom });
  };

  const onUp = () => {
    if (drag.current) {
      drag.current = null;
      setDragging(false);
      try {
        localStorage.setItem(KEY, JSON.stringify(posRef.current));
      } catch {}
    }
  };

  const onClick = () => {
    if (drag.current && drag.current.moved) return;
    if (typeof window !== 'undefined' && window.history.length > 1) router.back();
    else router.push('/musica');
  };

  return (
    <button
      ref={ref}
      className={'bfab' + (dragging ? ' is-drag' : '')}
      style={{ right: pos.right, bottom: pos.bottom }}
      onPointerDown={onDown}
      onPointerMove={onMove}
      onPointerUp={onUp}
      onClick={onClick}
      aria-label="Volver atrás"
      title="Volver atrás"
    >
      <span className="bf-arr">←</span>
      VOLVER
    </button>
  );
}