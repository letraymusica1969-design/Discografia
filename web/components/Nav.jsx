'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Nav() {
  const [open, setOpen] = useState(false);
  return (
    <header className="nav">
      <Link href="/" className="nav-logo">SAN<span>COUGAR</span></Link>
      <nav className={`nav-links ${open ? 'open' : ''}`}>
        <Link href="/" onClick={() => setOpen(false)}>Now</Link>
        <Link href="/musica" onClick={() => setOpen(false)}>Musica</Link>
        <Link href="/#acerca" onClick={() => setOpen(false)}>Acerca</Link>
        <Link href="/#unete" className="btn-ghost" onClick={() => setOpen(false)}>Unirte</Link>
      </nav>
      <button className="burger" onClick={() => setOpen(!open)} aria-label="Menu">
        <span /><span /><span />
      </button>
    </header>
  );
}