import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-main">
        <div>
          <p className="footer-logo">SANDRO SAAVEDRA</p>
          <p className="footer-tag">Canciones de una ciudad — Box set de 5 volúmenes</p>
        </div>
        <div className="footer-links">
          <Link href="/musica">Musica</Link>
          <Link href="/">Now</Link>
          <Link href="/#acerca">Acerca</Link>
        </div>
        <div className="footer-credits">
          <p>Música y letra: Sandro Saavedra</p>
          <p>Arreglos: Estudio Central</p>
          <p>Producción: El Desván del Vinilo — 2026</p>
        </div>
      </div>
      <div className="footer-bar">
        <span>© 2026 Sandro Saavedra</span>
        <span>33⅓ RPM — Estéreo</span>
      </div>
    </footer>
  );
}