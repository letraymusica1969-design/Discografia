import Link from 'next/link';
import DiscCard from '../components/DiscCard';
import Join from '../components/Join';
import { getDiscos } from '../lib/data';
import { COVER_VERSION } from '../lib/version';

const MARQUEE = [
  'MEDIANOCHE',
  'CIUDAD DE NEON',
  'OCHENTAS',
  'LLAMAS',
  'EUFORIA',
  'CANCIONES DE UNA CIUDAD',
  'SANDRO SAAVEDRA',
];

export default function Home() {
  const discos = getDiscos();
  const total = discos.reduce((a, d) => a + d.tracklist.length, 0);
  const cov = (i) => `/covers/${discos[i].slug}_front.jpg?${COVER_VERSION}`;
  const run = (k) => (
    <div key={k} className="ticker-run">
      {MARQUEE.map((t, i) => (
        <span key={i} className="ticker-item">{t}<i aria-hidden>✦</i></span>
      ))}
    </div>
  );

  return (
    <>
      <section className="hero">
        <div className="hero-bg" aria-hidden />
        <div className="hero-fx" aria-hidden>
          <div className="hero-vinyl hv-home">
            <span className="hv-shine" />
            <span className="hv-label">♪</span>
          </div>
          <div className="cover-pile">
            <img className="cp cp-1" src={cov(0)} alt="" />
            <img className="cp cp-2" src={cov(2)} alt="" />
            <img className="cp cp-3" src={cov(4)} alt="" />
          </div>
          <span className="pile-chip">BOX SET · 6 DISCOS · 2026</span>
          <span className="bk bk-1" /><span className="bk bk-2" /><span className="bk bk-3" />
        </div>
        <div className="hero-inner">
          <p className="hero-kicker">SANDRO SAAVEDRA · 2026</p>
          <h1 aria-label="Sandro Saavedra">
            SANDRO<br />
            <span className="thin">SAAVEDRA</span>
          </h1>
          <p className="hero-sub">
            Canciones de una ciudad — un box set de seis discos, {total} canciones.
          </p>
          <div className="hero-cta">
            <Link href="/musica" className="primary">Explorar la música</Link>
            <a href="#now" className="secondary">Novedades</a>
          </div>
        </div>
      </section>

      <div className="ticker" aria-hidden>{run('a')}{run('b')}</div>

      <section id="now" className="section">
        <p className="section-lbl">AHORA</p>
        <h2>Novedades</h2>
        <div className="now-grid">
          <article className="news-card" style={{ '--accent': 'var(--gold)' }}>
            <p className="date">BOX SET · 2026</p>
            <h3>Canciones de una ciudad</h3>
            <p>
              El box set completo llega en seis volúmenes: Medianoche, Ciudad de Neon, Ochentas,
              Llamas, Euforia y Directo. Vinilo 33⅓, estéreo, con libreto y código de barras.
            </p>
            <Link href="/musica" className="more">Ver la colección →</Link>
          </article>
          <article className="news-card" style={{ '--accent': '#ff3f9e' }}>
            <p className="date">PRIMER EXTRACTO · 2026</p>
            <h3>Medianoche</h3>
            <p>
              Dieciocho baladas que se escuchan a oscuras. El volumen de apertura del box, con la
              portada de luna de niebla.
            </p>
            <Link href="/disco/Disco_1_Medianoche" className="more">Escuchar / ver →</Link>
          </article>
          <article className="news-card" style={{ '--accent': '#00d9ff' }}>
            <p className="date">EL CLUB</p>
            <h3>Unirte al Desván</h3>
            <p>
              Material de archivo, historias de cada tema y acceso temprano a las próximas
              publicaciones de Sandro Saavedra.
            </p>
            <a href="#unete" className="more">Unirme →</a>
          </article>
        </div>
      </section>

      <section id="musica" className="section">
        <p className="section-lbl">MÚSICA</p>
        <h2>La colección</h2>
        <div className="music-grid">
          {discos.map((d, i) => (
            <DiscCard key={d.slug} d={d} index={i} />
          ))}
        </div>
      </section>

      <section id="acerca" className="section">
        <p className="section-lbl">ACERCA</p>
        <h2>El autor</h2>
        <div className="acerca">
          <p className="quote">«</p>
          <p>
            Sandro Saavedra escribe, compone y arregla. «Canciones de una ciudad» reúne setenta y
            cinco canciones de la balada nocturna a la euforia del final de fiesta.
          </p>
          <p>
            Seis discos — Medianoche, Ciudad de Neon, Ochentas, Llamas, Euforia y Directo —
            trazados como una sola noche en la ciudad. Cada volumen tiene su portada, su tracklist
            y su propio estado de ánimo.
          </p>
        </div>
      </section>

      <Join />
    </>
  );
}