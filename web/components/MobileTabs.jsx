'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const ICON = {
  home: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M4 10.5 12 3.5l8 7" />
      <path d="M5.5 9.5V20a.8.8 0 0 0 .8.8h11.4a.8.8 0 0 0 .8-.8V9.5" />
      <path d="M10 20v-5.2a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1V20" />
    </svg>
  ),
  disc: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none" />
      <path d="M13 4.2a8 8 0 0 1 6.4 6.4" strokeLinecap="round" />
    </svg>
  ),
  user: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <circle cx="12" cy="8" r="3.6" />
      <path d="M4.5 20c1.4-3.6 4.3-5.4 7.5-5.4s6.1 1.8 7.5 5.4" />
    </svg>
  ),
  mail: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="3" y="5.5" width="18" height="13" rx="2.4" />
      <path d="m3.5 7.5 8.5 5.7 8.5-5.7" />
    </svg>
  ),
};

export default function MobileTabs() {
  const path = usePathname() || '/';
  const isHome = path === '/';
  const isArchive = path === '/musica' || path.startsWith('/disco');
  return (
    <nav className="mtabs" aria-label="Navegación principal">
      <Link href="/" className={'mtab' + (isHome ? ' on' : '')} aria-current={isHome ? 'page' : undefined}>
        {ICON.home}
        <span>Inicio</span>
      </Link>
      <Link href="/musica" className={'mtab' + (isArchive ? ' on' : '')} aria-current={isArchive ? 'page' : undefined}>
        {ICON.disc}
        <span>Archivo</span>
      </Link>
      <Link href="/#acerca" className="mtab">
        {ICON.user}
        <span>Acerca</span>
      </Link>
      <Link href="/#unete" className="mtab">
        {ICON.mail}
        <span>Club</span>
      </Link>
    </nav>
  );
}