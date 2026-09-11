import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getDiscos, getDisco, fmtTime } from '../../../lib/data';
import { COVER_VERSION } from '../../../lib/version';

export function generateStaticParams() {
  return getDiscos().map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }) {
  const d = getDisco((await params).slug);
  return { title: d ? `${d.titulo} — Sandro Saavedra` : 'Disco' };
}

export default async function DiscoPage({ params }) {
  const d = getDisco((await params).slug);
  if (!d) notFound();
  const totalTracks = d.tracklist.length;
  const dur = d.totalDur;
  return (
    <>
      <section className="disco-hero">
        <img src={`/covers/${d.slug}_front.jpg?${COVER_VERSION}`} alt={`${d.titulo} — portada`} />
        <div>
          <p className="kick">BOX SET · VINILO · 2026 · VOL.{String(d.numero).padStart(2, '0')}</p>
          <h1>{d.titulo}</h1>
          <p className="sub">{d.subtitulo}</p>
          <span className="stat">{totalTracks} canciones</span>
          <span className="stat">{fmtTime(dur)}</span>
          <span className="stat">{d.ambito}</span>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <p className="section-lbl">TRACKLIST</p>
        <ol className="page-disco-tracks">
          {d.tracklist.map((t) => (
            <li key={t.n}>
              <span className="t-n">{String(t.n).padStart(2, '0')}</span>
              <span className="t-t">{t.titulo}</span>
              <span className="t-bpm">{t.bpm ? `${t.bpm.toFixed(0)} BPM` : ''}</span>
              <span className="t-d">{fmtTime(t.duracion)}</span>
            </li>
          ))}
        </ol>
        <div style={{ marginTop: 26, fontFamily: 'Agency', letterSpacing: '0.15em' }}>
          <Link href="/musica" style={{ color: 'var(--gold)' }}>← Volver al archivo</Link>
        </div>
      </section>

      <div className="disco-backback">
        <img src={`/covers/${d.slug}_back.jpg?${COVER_VERSION}`} alt={`${d.titulo} — dorso`} />
      </div>
    </>
  );
}