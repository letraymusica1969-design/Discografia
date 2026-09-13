import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getDiscos, getDisco, fmtTime } from '../../../lib/data';
import DiscoPlayer from '../../../components/DiscoPlayer';
import BackFab from '../../../components/BackFab';
import { COVER_VERSION } from '../../../lib/version';

export function generateStaticParams() {
  return getDiscos().map((d) => ({ slug: d.slug }));
}

export async function generateMetadata({ params }) {
  const d = getDisco((await params).slug);
  return { title: d ? `${d.titulo} — San Cougar` : 'Disco' };
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
        <DiscoPlayer tracks={d.tracklist} slug={d.slug} titulo={d.titulo} />
        <div style={{ marginTop: 26, fontFamily: 'Agency', letterSpacing: '0.15em' }}>
          <Link href="/musica" style={{ color: 'var(--gold)' }}>← Volver al archivo</Link>
        </div>
      </section>

      <div className="disco-backback">
        <img src={`/covers/${d.slug}_back.jpg?${COVER_VERSION}`} alt={`${d.titulo} — dorso`} />
      </div>

      <BackFab />
    </>
  );
}