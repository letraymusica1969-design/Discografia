import DiscoRow from '../../components/DiscoRow';
import { getDiscos } from '../../lib/data';

export const metadata = {
  title: 'Música — Sandro Saavedra',
  description: 'Archivo musical: el box set Canciones de una Ciudad, volúmenes 1 a 5.',
};

export default function Musica() {
  const discos = getDiscos();
  const marquee = discos.map((d) => d.titulo.toUpperCase());
  const run = (key) => (
    <div key={key} className="ticker-run">
      {marquee.map((t, i) => (
        <span key={i} className="ticker-item">{t}<i aria-hidden>✦</i></span>
      ))}
    </div>
  );
  return (
    <>
      <section className="page-hero">
        <div className="hero-bg" aria-hidden />
        <div className="hero-vinyl" aria-hidden>
          <span className="hv-shine" />
          <span className="hv-label">♪</span>
        </div>
        <div className="hero-bokeh" aria-hidden>
          <span className="bk bk-1" /><span className="bk bk-2" /><span className="bk bk-3" /><span className="bk bk-4" />
        </div>
        <div className="hero-inner">
          <p className="section-lbl">MÚSICA</p>
          <h1>Archivo</h1>
          <p className="page-hero-sub">
            El box set <em>Canciones de una ciudad</em> — seis volúmenes, setenta y cuatro canciones.
          </p>
        </div>
      </section>
      <div className="ticker" aria-hidden>{run('a')}{run('b')}</div>
      <div className="archive">
        {discos.map((d, i) => (
          <DiscoRow key={d.slug} d={d} index={i} />
        ))}
      </div>
    </>
  );
}